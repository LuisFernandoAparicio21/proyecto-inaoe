# app.py

import streamlit as st
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from pathlib import Path
import time
import torch
import requests

# --- Importaciones de Modelos Específicos ---
# Se mantienen las importaciones para que la estructura sea extensible en el futuro.
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_ollama import Ollama
    # Las siguientes se pueden añadir a requirements.txt cuando se activen sus modelos
    from langchain_groq import ChatGroq
    from langchain_together import Together
except ImportError as e:
    st.error(f"Error al importar una librería de LangChain: {e}. Por favor, ejecuta 'pip install -r requirements.txt'")
    st.stop()

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
    # --- Modelos Activos ---
    "mistral:7b": {
        "provider": "ollama", 
        "info": "🏆 Local - Excelente para investigación, gratis, requiere 4GB RAM."
    },
    "gemini-1.5-flash": {
        "provider": "google", 
        "info": "🟢 API Google - Rápido y preciso, requiere API key, 15 req/min gratis."
    },
    "gemini-1.5-pro": {
        "provider": "google", 
        "info": "✨ API Google - Máxima calidad de razonamiento, más lento y costoso."
    },

    # --- Modelos  ---
    # "llama3.2:3b": {
    #     "provider": "ollama", 
    #     "info": "🟢 Local - Buen balance calidad/velocidad, gratis, 2GB RAM."
    # },
    # "llama3-8b-8192": {
    #     "provider": "groq", 
    #     "info": "🟡 API Groq - Muy rápido, requiere API key."
    # },
    # "together/llama-2-7b-chat": {
    #     "provider": "together", 
    #     "info": "🟢 API Together - $25 créditos gratis, alta calidad."
    # },
}

PROMPT_TEMPLATE = """Eres un asistente experto en investigación científica del INAOE.
... (tu prompt completo va aquí, lo he omitido por brevedad) ...
RESPUESTA:"""

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

@st.cache_data(ttl=300) # Cachear por 5 minutos para no verificar constantemente
def verificar_ollama():
    """Verifica si el servicio de Ollama está activo."""
    try:
        requests.get("http://localhost:11434", timeout=3)
        return True
    except requests.ConnectionError:
        return False

def format_docs(docs):
    """Formatea los documentos recuperados para el prompt."""
    return "\n\n".join(doc.page_content for doc in docs)

# --- Fábrica de LLMs (LLM Factory) ---

def get_llm(modelo, temperature, timeout):
    """Fábrica que devuelve una instancia del LLM seleccionado. La estructura está lista para más proveedores."""
    config = MODEL_CONFIG.get(modelo, {})
    provider = config.get("provider")

    if provider == "google":
        if 'GOOGLE_API_KEY' not in st.secrets:
            st.error("🚨 Falta la API Key de Google en .streamlit/secrets.toml.")
            return None
        return ChatGoogleGenerativeAI(model=modelo.split('/')[-1], api_key=st.secrets["GOOGLE_API_KEY"], temperature=temperature)
    
    elif provider == "ollama":
        if not verificar_ollama():
            st.error("🚨 Ollama no está ejecutándose. Inicia el servicio de Ollama para usar este modelo.")
            return None
        return Ollama(model=modelo, temperature=temperature, timeout=timeout)
        
    # --- Lógica para futuros proveedores (ya está lista) ---
    elif provider == "groq":
        if 'GROQ_API_KEY' not in st.secrets:
            st.error("🚨 Falta la API Key de Groq en .streamlit/secrets.toml.")
            return None
        return ChatGroq(api_key=st.secrets["GROQ_API_KEY"], model=modelo.split('/')[-1], temperature=temperature)

    elif provider == "together":
        if 'TOGETHER_API_KEY' not in st.secrets:
            st.error("🚨 Falta la API Key de Together AI en .streamlit/secrets.toml.")
            return None
        return Together(model=modelo, api_key=st.secrets["TOGETHER_API_KEY"], temperature=temperature)
        
    else:
        st.error(f"🚨 Proveedor '{provider}' para el modelo '{modelo}' no está configurado.")
        return None

# --- Funciones de la Interfaz de Usuario ---

def render_sidebar():
    """Renderiza la barra lateral con todas las opciones de configuración."""
    st.sidebar.header("⚙️ Configuración")
    
    modelo_seleccionado = st.sidebar.selectbox(
        "Selecciona el modelo:",
        list(MODEL_CONFIG.keys()),
        index=0
    )
    
    
    assert modelo_seleccionado is not None, "selectbox no debería devolver None con las opciones dadas"

    # Ahora esta línea es segura para el analizador
    st.sidebar.info(MODEL_CONFIG[modelo_seleccionado]["info"])

    with st.sidebar.expander("🔧 Configuración Avanzada"):
        chunk_size = st.slider("Documentos a consultar", 3, 10, 5)
        temperature = st.slider("Creatividad", 0.0, 1.0, 0.2)
        timeout = st.slider("Timeout (segundos)", 30, 300, 120)
        
    return modelo_seleccionado, chunk_size, temperature, timeout

# --- Flujo Principal de la Aplicación ---

def main():
    st.title("Asistente de Investigación INAOE 🤖")
    st.write("Hazme preguntas sobre los documentos del INAOE y te ayudaré a encontrar la información.")

    modelo_sel, chunk_size, temp, timeout = render_sidebar()

    db = cargar_base_datos()
    if db is None:
        return # Detiene la ejecución si la base de datos no se carga
        
    llm = get_llm(modelo_sel, temp, timeout)
    if llm is None:
        return # Detiene la ejecución si el modelo no se puede configurar

    try:
        # Crear el retriever - validar que db no sea None
        if db is None:
            st.error("❌ Error: La base de datos no se pudo cargar correctamente.")
            return
        retriever = db.as_retriever(search_kwargs={"k": chunk_size})
        
        # Crear el prompt template
        prompt = PromptTemplate.from_template(PROMPT_TEMPLATE)
        
        # Crear la nueva cadena RAG con LCEL
        def create_rag_chain():
            def rag_invoke(question):
                # Obtener documentos relevantes
                docs = retriever.get_relevant_documents(question)
                context = format_docs(docs)
                
                # Crear el prompt
                formatted_prompt = prompt.format(context=context, question=question)
                
                # Obtener respuesta del LLM
                if llm is None:
                    return {"context": context, "question": question, "answer": "Error: LLM no disponible"}
                response = llm.invoke(formatted_prompt)
                # Convertir la respuesta a string si es necesario
                if hasattr(response, 'content'):
                    answer = response.content
                else:
                    answer = str(response)
                
                return {
                    "context": context,
                    "question": question,
                    "answer": answer
                }
            return rag_invoke
        
        rag_chain_with_source = create_rag_chain()
    except Exception as e:
        st.error(f"Error al crear la cadena de QA: {e}")
        return

    st.markdown("---")
    if 'pregunta' not in st.session_state:
        st.session_state.pregunta = ""

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
                # Invocación simplificada con la nueva cadena LCEL
                result = rag_chain_with_source(pregunta)
                end_time = time.time()

                st.markdown("### 📝 Respuesta:")
                st.write(result.get("answer", "No se pudo generar una respuesta."))
                
                st.metric("⏱️ Tiempo de respuesta", f"{end_time - start_time:.2f} segundos")

                # Mostrar fuentes consultadas
                if result.get("context") and "No se encontró información relevante" not in result.get("answer", ""):
                    with st.expander("📚 Ver fuentes consultadas"):
                        st.write(result.get("context", ""))

            except Exception as e:
                st.error(f"❌ Error al generar la respuesta: {e}")

if __name__ == "__main__":
    main()