# procesar_docs_mejorado.py

import os
import json
import logging
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import shutil

# --- Configuración Centralizada ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Usar pathlib para un manejo de rutas más robusto y legible
RUTA_PROYECTO = Path(__file__).resolve().parent.parent
DIR_DOCS = RUTA_PROYECTO / "documentos"
DIR_DB_FAISS = RUTA_PROYECTO / "indice_faiss"
DIR_DB_TEMP = RUTA_PROYECTO / "indice_faiss_temp"
ARCHIVO_REGISTRO = RUTA_PROYECTO / "processed_files.json"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# --- Funciones de Ayuda ---

def cargar_registro_archivos():
    """Carga el registro de archivos procesados desde un JSON."""
    if not ARCHIVO_REGISTRO.exists():
        return {}
    with open(ARCHIVO_REGISTRO, 'r') as f:
        return json.load(f)

def guardar_registro_archivos(registro):
    """Guarda el registro actualizado de archivos procesados."""
    with open(ARCHIVO_REGISTRO, 'w') as f:
        json.dump(registro, f, indent=4)

def obtener_archivos_a_procesar(registro):
    """Determina qué archivos son nuevos o han sido modificados."""
    archivos_nuevos = []
    if not DIR_DOCS.exists():
        logging.error(f"El directorio de documentos '{DIR_DOCS}' no existe.")
        return []
        
    for archivo_pdf in DIR_DOCS.glob("*.pdf"):
        nombre_archivo = str(archivo_pdf)
        ultima_modificacion = os.path.getmtime(nombre_archivo)
        
        if nombre_archivo not in registro or registro[nombre_archivo] < ultima_modificacion:
            archivos_nuevos.append(nombre_archivo)
            registro[nombre_archivo] = ultima_modificacion
            
    return archivos_nuevos

def procesar_lote_documentos(rutas_archivos):
    """Carga y divide en chunks un lote de documentos PDF."""
    documentos = []
    for ruta in rutas_archivos:
        try:
            loader = PyPDFLoader(ruta)
            documentos.extend(loader.load())
            logging.info(f"Cargado: {Path(ruta).name}")
        except Exception as e:
            logging.error(f"Error cargando el archivo {ruta}: {e}")
            continue # Salta al siguiente archivo si uno falla
    
    if not documentos:
        return []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    return splitter.split_documents(documentos)

# --- Flujo Principal ---

def main():
    """
    Flujo principal para procesar documentos de forma robusta e incremental.
    """
    logging.info("🚀 Iniciando proceso de actualización de la base de datos vectorial.")
    
    registro_archivos = cargar_registro_archivos()
    archivos_a_procesar = obtener_archivos_a_procesar(registro_archivos)
    
    if not archivos_a_procesar and DIR_DB_FAISS.exists():
        logging.info("✅ No hay documentos nuevos o modificados. La base de datos está actualizada.")
        return

    try:
        # Paso 1: Cargar y procesar los documentos nuevos/modificados
        logging.info(f"Se encontraron {len(archivos_a_procesar)} archivos para procesar.")
        chunks_nuevos = procesar_lote_documentos(archivos_a_procesar)
        
        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        
        # Eliminar el directorio temporal si existe de una ejecución anterior fallida
        if DIR_DB_TEMP.exists():
            shutil.rmtree(DIR_DB_TEMP)

        # Paso 2: Cargar la base de datos existente o crear una nueva
        if DIR_DB_FAISS.exists() and chunks_nuevos:
            logging.info("Cargando base de datos existente para fusionar...")
            db_existente = FAISS.load_local(str(DIR_DB_FAISS), embeddings, allow_dangerous_deserialization=True)
            db_existente.add_documents(chunks_nuevos)
            db_final = db_existente
        elif chunks_nuevos:
            logging.info("Creando una nueva base de datos vectorial...")
            db_final = FAISS.from_documents(chunks_nuevos, embeddings)
        else:
            logging.info("No hay chunks para procesar. Finalizando.")
            return

        # Paso 3: Guardar en un directorio temporal (Principio de Atomicidad)
        logging.info(f"Guardando índice actualizado en directorio temporal: {DIR_DB_TEMP}")
        db_final.save_local(str(DIR_DB_TEMP))
        
        # Paso 4: Reemplazo Atómico
        # Si todo fue exitoso, eliminamos el directorio antiguo y renombramos el nuevo.
        logging.info("Reemplazando la base de datos antigua con la nueva versión...")
        if DIR_DB_FAISS.exists():
            shutil.rmtree(DIR_DB_FAISS)
        os.rename(DIR_DB_TEMP, DIR_DB_FAISS)
        
        # Paso 5: Actualizar el registro de archivos procesados
        guardar_registro_archivos(registro_archivos)
        
        logging.info(f"🎉 ¡Proceso completado! Base de datos guardada en: {DIR_DB_FAISS}")

    except Exception as e:
        logging.error(f"❌ Ocurrió un error crítico durante el proceso: {e}")
        logging.info("La operación fue abortada. La base de datos original no ha sido modificada.")
        # Limpiar el directorio temporal en caso de error
        if DIR_DB_TEMP.exists():
            shutil.rmtree(DIR_DB_TEMP)
            
if __name__ == "__main__":
    main()