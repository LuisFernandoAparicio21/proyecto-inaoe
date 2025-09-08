from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import os
from pathlib import Path
import logging


# --- Configuración ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def cargar_documentos(directorio_docs):
    """Carga todos los PDFs del directorio especificado."""
    documentos = []
    for archivo in os.listdir(directorio_docs):
        if archivo.endswith('.pdf'):
            ruta_completa = os.path.join(directorio_docs, archivo)
            loader = PyPDFLoader(ruta_completa)
            logging.info(f"Cargando documento: {archivo}")
            documentos.extend(loader.load())
    return documentos

def dividir_texto(documentos):
    """Divide los documentos en chunks más pequeños."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    return splitter.split_documents(documentos)

def crear_base_vectorial(chunks):
    """Crea una base de datos vectorial con los chunks de texto."""
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    db = FAISS.from_documents(chunks, embeddings)
    return db

def main():
    # Usar pathlib para un manejo de rutas más robusto y legible
    ruta_proyecto = Path(__file__).resolve().parent.parent
    dir_docs = ruta_proyecto / "documentos"
    ruta_db_local = ruta_proyecto / "indice_faiss"
    
    logging.info(f"Buscando documentos en: {dir_docs}")

    if not dir_docs.exists() or not any(dir_docs.glob("*.pdf")):
        logging.error(f"La carpeta '{dir_docs}' no existe o no contiene archivos PDF.")
        logging.info("Por favor, crea la carpeta 'documentos' en la raíz del proyecto y añade tus archivos PDF.")
        return
    
    # Cargar documentos
    logging.info("Cargando documentos...")
    docs = cargar_documentos(dir_docs)
    if not docs:
        logging.warning("No se pudo cargar ningún contenido de los archivos PDF.")
        return
    
    # Dividir en chunks
    logging.info(f"Dividiendo {len(docs)} páginas en chunks...")
    chunks = dividir_texto(docs)
    
    # Crear y guardar la base vectorial
    logging.info(f"Creando base de datos vectorial con {len(chunks)} chunks...")
    db = crear_base_vectorial(chunks)
    db.save_local(str(ruta_db_local))
    
    logging.info(f"¡Proceso completado! Base de datos guardada en: {ruta_db_local}")

if __name__ == "__main__":
    main()