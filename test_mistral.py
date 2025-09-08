#!/usr/bin/env python3
"""
Script de prueba para Mistral 7B con la base de datos RAG del INAOE
"""

import sys
from pathlib import Path
import time

# Añadir el directorio src al path
sys.path.append(str(Path(__file__).parent / "src"))

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_community.llms.ollama import Ollama

def cargar_base_datos():
    """Carga la base de datos vectorial."""
    ruta_proyecto = Path(__file__).resolve().parent
    ruta_db = ruta_proyecto / "indice_faiss"
    
    if not ruta_db.exists():
        print(f"❌ No se encontró la base de datos en: {ruta_db}")
        print("💡 Ejecuta primero: `python src/procesar_docs.py`")
        return None
    
    try:
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        db = FAISS.load_local(str(ruta_db), embeddings, allow_dangerous_deserialization=True)
        print(f"✅ Base de datos cargada: {db.index.ntotal} documentos")
        return db
    except Exception as e:
        print(f"❌ Error al cargar la base de datos: {e}")
        return None

def configurar_mistral():
    """Configura Mistral 7B."""
    try:
        llm = Ollama(
            model="mistral:7b",
            temperature=0.2,
            timeout=120
        )
        print("✅ Mistral 7B configurado correctamente")
        return llm
    except Exception as e:
        print(f"❌ Error al configurar Mistral 7B: {e}")
        print("💡 Asegúrate de que Ollama esté ejecutándose: `ollama serve`")
        return None

def probar_preguntas(qa_chain):
    """Prueba diferentes preguntas con Mistral 7B."""
    
    preguntas_prueba = [
        "¿Qué es el INAOE?",
        "¿Cuáles son las áreas de investigación principales?",
        "¿Qué trabajos se han hecho sobre óptica?",
        "¿Qué dice sobre CONIELECOMP 2013?",
        "¿Qué programas de posgrado ofrece el INAOE?"
    ]
    
    print("\n" + "="*60)
    print("🧪 PRUEBAS CON MISTRAL 7B")
    print("="*60)
    
    for i, pregunta in enumerate(preguntas_prueba, 1):
        print(f"\n📝 Pregunta {i}: {pregunta}")
        print("-" * 50)
        
        try:
            start_time = time.time()
            result = qa_chain.invoke({"query": pregunta})
            end_time = time.time()
            
            respuesta = result.get("result", "No se encontró respuesta.")
            documentos = result.get("source_documents", [])
            
            print(f"⏱️  Tiempo: {end_time - start_time:.2f}s")
            print(f"📄 Documentos consultados: {len(documentos)}")
            print(f"🤖 Respuesta: {respuesta}")
            
            if documentos:
                print(f"📚 Fuentes:")
                for j, doc in enumerate(documentos, 1):
                    fuente = doc.metadata.get('source', 'Documento')
                    pagina = doc.metadata.get('page', 'N/A')
                    print(f"   {j}. {fuente} (Página: {pagina})")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("\n" + "="*60)

def main():
    print("🚀 Iniciando prueba de Mistral 7B con base de datos INAOE")
    
    # Cargar base de datos
    db = cargar_base_datos()
    if db is None:
        return
    
    # Configurar Mistral 7B
    llm = configurar_mistral()
    if llm is None:
        return
    
    # Crear cadena QA
    try:
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=db.as_retriever(search_kwargs={"k": 5}),
            return_source_documents=True
        )
        print("✅ Cadena QA creada correctamente")
    except Exception as e:
        print(f"❌ Error al crear cadena QA: {e}")
        return
    
    # Probar preguntas
    probar_preguntas(qa_chain)
    
    print("\n🎉 ¡Prueba completada!")
    print("💡 Para usar en Streamlit, selecciona 'mistral:7b' en la interfaz")

if __name__ == "__main__":
    main()

