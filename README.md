# Asistente de Investigación INAOE 🤖

Un sistema de preguntas y respuestas basado en RAG (Retrieval-Augmented Generation) que permite consultar documentos del INAOE de manera inteligente.

## 🚀 Características

- **Múltiples modelos de IA**: Soporte para Google Gemini, Groq, y Ollama
- **Búsqueda semántica**: Encuentra información relevante en documentos PDF
- **Interfaz web intuitiva**: Aplicación Streamlit fácil de usar
- **Configuración flexible**: Ajusta parámetros según tus necesidades
- **Manejo robusto de errores**: Información clara sobre problemas y soluciones

## 📋 Requisitos

- Python 3.8+
- Dependencias listadas en `requirements.txt`
- Para modelos locales: Ollama instalado
- Para APIs remotas: Claves de API correspondientes

## 🛠️ Instalación

1. **Clonar el repositorio**:
```bash
git clone <url-del-repositorio>
cd proyecto_rag_inaoe
```

2. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

3. **Configurar API keys** (opcional):
Crear archivo `.streamlit/secrets.toml`:
```toml
GOOGLE_API_KEY = "tu-api-key-de-google"
GROQ_API_KEY = "tu-api-key-de-groq"
```

4. **Procesar documentos**:
```bash
cd src
python procesar_docs.py
```

5. **Ejecutar la aplicación**:
```bash
streamlit run app.py
```

## 🔧 Configuración

### Modelos Disponibles

| Modelo | Proveedor | Tipo | Costo | Velocidad | Precisión |
|--------|-----------|------|-------|-----------|-----------|
| gemini-1.5-flash | Google | API Remota | Gratis | Rápido | Alta |
| llama3-8b-8192 | Groq | API Remota | Pago | Muy rápido | Alta |
| gemma-7b-it | Groq | API Remota | Pago | Rápido | Media-Alta |
| qwen3:4b | Ollama | Local | Gratis | Lento | Media |
| llama3.2:1b | Ollama | Local | Gratis | Rápido | Media |

### Parámetros Ajustables

- **Número de documentos**: Controla cuántos documentos se consultan (3-10)
- **Creatividad**: Ajusta la temperatura del modelo (0.0-1.0)
- **Timeout**: Tiempo máximo de espera para respuestas (30-300s)

## 📁 Estructura del Proyecto

```
proyecto_rag_inaoe/
├── documentos/           # PDFs a procesar
├── indice_faiss/        # Base de datos vectorial
├── src/
│   ├── app.py           # Aplicación principal
│   ├── procesar_docs.py # Procesamiento de documentos
│   └── utils.py         # Utilidades y validaciones
├── requirements.txt     # Dependencias
└── README.md           # Este archivo
```

## 🔍 Uso

1. **Abrir la aplicación** en tu navegador (http://localhost:8501)
2. **Seleccionar modelo** en la barra lateral
3. **Ajustar configuración** según necesites
4. **Hacer preguntas** sobre los documentos del INAOE
5. **Revisar fuentes** para verificar la información

### Ejemplos de Preguntas

- ¿Qué es el INAOE?
- ¿Cuáles son las áreas de investigación?
- ¿Qué programas de posgrado ofrece?
- ¿Qué trabajos se han hecho sobre óptica?
- ¿Qué dice sobre CONIELECOMP 2013?

## 🐛 Solución de Problemas

### Error: "Base de datos no encontrada"
```bash
cd src
python procesar_docs.py
```

### Error: "Ollama no está ejecutándose"
```bash
ollama serve
```

### Error: "API keys no configuradas"
Crear archivo `.streamlit/secrets.toml` con las claves correspondientes.

### Error: "Módulo no disponible"
```bash
pip install langchain-groq
```

### Error: "Timeout"
- Usar un modelo más rápido
- Reducir el número de documentos consultados
- Hacer preguntas más específicas

## 🔄 Mejoras Recientes

### Versión 2.0 - Correcciones Implementadas

1. **Corrección del problema L1**: Mejorada la distribución de columnas en la interfaz
2. **Detección automática de GPU**: Uso de CUDA cuando está disponible
3. **Validación de preguntas**: Verificación de que las preguntas sean apropiadas
4. **Métricas de rendimiento**: Tiempo de respuesta y estadísticas
5. **Manejo robusto de errores**: Mensajes informativos y soluciones
6. **Configuración avanzada**: Parámetros ajustables en tiempo real
7. **Verificación de servicios**: Comprobación automática de Ollama y APIs
8. **Interfaz mejorada**: Mejor UX con botones de limpieza y ejemplos

### Problemas Corregidos

- ❌ **Línea 134**: `col1, col2, col3 = st.columns([1, 1, 1])` → ✅ Distribución mejorada
- ❌ **Falta de validación**: → ✅ Validación de preguntas implementada
- ❌ **Manejo de errores básico**: → ✅ Sistema robusto de manejo de errores
- ❌ **Configuración fija**: → ✅ Parámetros ajustables
- ❌ **Sin métricas**: → ✅ Métricas de rendimiento en tiempo real

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 📞 Soporte

Para soporte técnico o preguntas:
- Abrir un issue en GitHub
- Contactar al equipo de desarrollo

---

**Desarrollado con ❤️ para la comunidad INAOE**