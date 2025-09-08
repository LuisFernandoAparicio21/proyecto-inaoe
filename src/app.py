import streamlit as st
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import PromptTemplate
from pathlib import Path
import time
import torch
import requests

# --- Importaciones de Modelos Específicos (Actualizadas) ---
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError as e:
    st.error(f"Error al importar langchain_google_genai: {e}. Instala con: 'pip install langchain-google-genai'")
    st.stop()

try:
    from langchain_ollama import ChatOllama
except ImportError as e:
    st.error(f"Error al importar langchain_ollama: {e}. Instala con: 'pip install langchain-ollama'")
    st.stop()

# --- Importaciones para la Cadena LCEL (Método Moderno) ---
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Asistente INAOE 🚀",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Constantes y Configuración de Modelos ---
RUTA_PROYECTO = Path(__file__).resolve().parent.parent
RUTA_DB = RUTA_PROYECTO / "indice_faiss"

MODEL_CONFIG = {
    "mistral:7b": {
        "provider": "ollama",
        "info": "🏆 Local - Excelente para investigación, gratis, requiere 4GB RAM."
    },
    "gemini-1.5-flash": {
        "provider": "google",
        "info": "🟢 API Google - Rápido y preciso, requiere API key, 15 req/min gratis."
    },
}

PROMPT_TEMPLATE = """Eres un asistente experto en investigación del INAOE. Tu tarea es responder a la pregunta del usuario de la forma más completa y precisa posible.

Para ello, debes seguir estas reglas:
1.  **COMBINA CONOCIMIENTO:** Fusiona tu propio conocimiento general sobre ciencia, tecnología y el INAOE con la información específica encontrada en los siguientes documentos de contexto.
2.  **PRIORIZA EL CONTEXTO:** Si la respuesta se encuentra en los documentos, dale prioridad a esa información para que la respuesta sea fundamentada.
3.  **USA CONOCIMIENTO GENERAL:** Si los documentos no contienen información relevante para la pregunta (o si el contexto está vacío), responde utilizando tu conocimiento general. No te limites a decir "no encontré información".
4.  **SÉ COMPLETO:** Proporciona respuestas detalladas y bien estructuradas, adecuadas para un público de investigadores.

A continuación, se presenta el contexto y la pregunta.

CONTEXTO DE LOS DOCUMENTOS:
{context}

PREGUNTA: {question}

RESPUESTA EXPERTA:"""


# --- Funciones de Carga y Configuración (Cacheadas) ---

@st.cache_resource
def cargar_base_datos():
    """Carga la base de datos vectorial FAISS de forma segura."""
    if not RUTA_DB.exists():
        st.error(f"❌ No se encontró la base de datos en: {RUTA_DB}")
        st.info("💡 Ejecuta primero: `python procesar_docs.py`")
        return None
    try:
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={'device': device}
        )
        return FAISS.load_local(str(RUTA_DB), embeddings, allow_dangerous_deserialization=True)
    except Exception as e:
        st.error(f"Error al cargar la base de datos: {e}")
        return None

@st.cache_data(ttl=300)
def verificar_ollama():
    """Verifica si el servicio de Ollama está activo."""
    try:
        requests.get("http://localhost:11434", timeout=3)
        return True
    except requests.ConnectionError:
        return False

# --- Fábrica de LLMs (LLM Factory) ---

def get_llm(modelo, temperature):
    """Fábrica que devuelve una instancia del LLM seleccionado."""
    config = MODEL_CONFIG.get(modelo, {})
    provider = config.get("provider")

    if provider == "google":
        if 'GOOGLE_API_KEY' not in st.secrets:
            st.error("🚨 Falta la API Key de Google en .streamlit/secrets.toml.")
            return None
        return ChatGoogleGenerativeAI(model=modelo, api_key=st.secrets["GOOGLE_API_KEY"], temperature=temperature)

    elif provider == "ollama":
        if not verificar_ollama():
            st.error("🚨 Ollama no está ejecutándose. Inicia el servicio de Ollama para usar este modelo.")
            return None
        return ChatOllama(model=modelo, temperature=temperature)

    else:
        st.error(f"🚨 Proveedor '{provider}' para el modelo '{modelo}' no está configurado.")
        return None

# --- Funciones de la Interfaz de Usuario ---

def render_sidebar():
    """Renderiza la barra lateral con la configuración esencial."""
    st.sidebar.header("⚙️ Configuración")
    modelo_seleccionado = st.sidebar.selectbox("Selecciona el modelo:", list(MODEL_CONFIG.keys()), index=0)

    assert modelo_seleccionado is not None
    st.sidebar.info(MODEL_CONFIG[modelo_seleccionado]["info"])

    chunk_size = 5
    temperature = 0.2

    return modelo_seleccionado, chunk_size, temperature

# --- Flujo Principal de la Aplicación ---

def format_docs(docs):
    """Formatea los documentos recuperados en una sola cadena de texto."""
    return "\n\n".join(doc.page_content for doc in docs)

def main():
    st.title("Asistente de Investigación INAOE 🤖")
    st.write("Hazme preguntas sobre los documentos del INAOE y te ayudaré a encontrar la información.")

    modelo_sel, chunk_size, temp = render_sidebar()

    db = cargar_base_datos()
    # --- INICIO DE LA SECCIÓN CORREGIDA (SOLUCIÓN ERROR #2 y #3) ---
    # Esta comprobación es CRUCIAL. Si db es None, detenemos la app.
    if db is None:
        st.warning("La base de datos no está disponible. No se pueden realizar consultas.")
        st.stop()
    # --- FIN DE LA SECCIÓN CORREGIDA ---

    llm = get_llm(modelo_sel, temp)
    if llm is None:
        st.stop()

    # Create retriever and chain only if db and llm are available
    if db is not None and llm is not None:
        try:
            retriever = db.as_retriever(search_kwargs={"k": chunk_size})
            prompt = PromptTemplate.from_template(PROMPT_TEMPLATE)

            rag_chain_with_source = RunnableParallel(
                {"context": retriever | format_docs, "question": RunnablePassthrough(), "docs": retriever}
            ).assign(answer=(
                RunnablePassthrough()
                | prompt
                | llm
                | StrOutputParser()
            ))

        except Exception as e:
            st.error(f"Error al crear la cadena de QA con LCEL: {e}")
            st.stop()
    else:
        st.error("No se puede crear la cadena de QA: la base de datos o el modelo no están disponibles.")
        st.stop()

    st.markdown("---")
    pregunta = st.text_input("🤔 ¿Qué te gustaría saber?", key="pregunta_input")

    col1, col2, _ = st.columns([1, 1, 3])
    buscar_presionado = col1.button("🔍 Buscar respuesta", type="primary")
    if col2.button("🧹 Limpiar"):
        st.session_state.pregunta_input = ""
        st.rerun()

    if buscar_presionado and pregunta:
        with st.spinner(f"🤖 Buscando respuesta con {modelo_sel}..."):
            start_time = time.time()
            try:
                result = rag_chain_with_source.invoke(pregunta)
                end_time = time.time()

                st.markdown("### 📝 Respuesta:")
                st.write(result.get("answer", "No se pudo generar una respuesta."))

                st.metric("⏱️ Tiempo de respuesta", f"{end_time - start_time:.2f} segundos")

                documentos = result.get("docs", [])
                if documentos:
                    with st.expander("📚 Ver fuentes consultadas"):
                        for doc in documentos:
                            st.info(f"Fuente: {doc.metadata.get('source', 'N/A')} - Página: {doc.metadata.get('page', 'N/A')}")

            except Exception as e:
                st.error(f"❌ Error al generar la respuesta: {e}")

if __name__ == "__main__":
    main()