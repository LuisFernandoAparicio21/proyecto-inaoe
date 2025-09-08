#!/usr/bin/env python3
"""
Script de prueba MEJORADO para Mistral 7B con base de datos RAG del INAOE
Ahora mezcla conocimiento general + documentos específicos
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
from langchain.prompts import PromptTemplate

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

def crear_cadena_qa_mejorada(llm, db):
    """Crea una cadena QA que mezcla conocimiento general + documentos."""
    
    # Prompt personalizado para mezclar conocimiento general + documentos
    prompt_template = """Eres un asistente experto en investigación científica del INAOE. 

CONTEXTO DE LOS DOCUMENTOS:
{context}

PREGUNTA: {question}

INSTRUCCIONES:
1. Responde en el MISMO IDIOMA de la pregunta
2. Usa tu conocimiento general sobre el tema
3. COMBINA tu conocimiento con la información de los documentos
4. Si los documentos no tienen información relevante, usa solo tu conocimiento general
5. Sé específico y detallado
6. Menciona las fuentes cuando sea relevante

RESPUESTA:"""

    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template=prompt_template
    )
    
    try:
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=db.as_retriever(search_kwargs={"k": 5}),
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt}
        )
        print("✅ Cadena QA mejorada creada correctamente")
        return qa_chain
    except Exception as e:
        print(f"❌ Error al crear cadena QA: {e}")
        return None

def probar_preguntas_mejoradas(qa_chain):
    """Prueba diferentes preguntas con la configuración mejorada."""
    
    preguntas_prueba = [
        "¿Qué es la investigación científica?",
        "¿Cuáles son las áreas de investigación principales del INAOE?",
        "¿Qué trabajos se han hecho sobre óptica en el INAOE?",
        "¿Qué dice sobre CONIELECOMP 2013?",
        "¿Qué programas de posgrado ofrece el INAOE?",
        "¿Cómo se relaciona la astronomía con la investigación en óptica?",
        "¿Qué es un CubeSat y cómo se investiga en el INAOE?"
    ]
    
    print("\n" + "="*70)
    print("🧪 PRUEBAS CON MISTRAL 7B MEJORADO")
    print("🎯 Ahora mezcla conocimiento general + documentos específicos")
    print("="*70)
    
    for i, pregunta in enumerate(preguntas_prueba, 1):
        print(f"\n📝 Pregunta {i}: {pregunta}")
        print("-" * 60)
        
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
                print(f"📚 Fuentes consultadas:")
                for j, doc in enumerate(documentos, 1):
                    fuente = doc.metadata.get('source', 'Documento')
                    pagina = doc.metadata.get('page', 'N/A')
                    print(f"   {j}. {fuente} (Página: {pagina})")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("\n" + "="*70)

def main():
    print("🚀 Iniciando prueba de Mistral 7B MEJORADO con base de datos INAOE")
    print("🎯 Ahora mezcla conocimiento general + documentos específicos")
    
    # Cargar base de datos
    db = cargar_base_datos()
    if db is None:
        return
    
    # Configurar Mistral 7B
    llm = configurar_mistral()
    if llm is None:
        return
    
    # Crear cadena QA mejorada
    qa_chain = crear_cadena_qa_mejorada(llm, db)
    if qa_chain is None:
        return
    
    # Probar preguntas
    probar_preguntas_mejoradas(qa_chain)
    
    print("\n🎉 ¡Prueba completada!")
    print("💡 Ahora Mistral 7B mezcla conocimiento general + documentos del INAOE")
    print("🌍 Responde en el idioma de la pregunta")
    print("🔬 Combina información de ambas fuentes")

if __name__ == "__main__":
    main()
