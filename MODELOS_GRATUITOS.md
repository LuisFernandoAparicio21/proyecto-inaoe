# 🤖 Modelos LLM Gratuitos para tu Proyecto RAG

## 🆓 Modelos Completamente Gratuitos

### 1. **Ollama (Local) - Recomendado para uso intensivo**

#### Instalación:
```bash
# Instalar Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Iniciar Ollama
ollama serve

# Descargar modelos (en otra terminal)
ollama pull llama3.2:1b
ollama pull llama3.2:3b
ollama pull qwen2.5:3b
ollama pull phi3:mini
ollama pull gemma2:2b
ollama pull mistral:7b
```

#### Modelos Recomendados:
- **llama3.2:1b** - ⚡ Muy rápido, 1GB RAM, bueno para tareas simples
- **llama3.2:3b** - ⚡ Rápido, 2GB RAM, mejor calidad
- **qwen2.5:3b** - 🌍 Excelente para español, 2GB RAM
- **phi3:mini** - ⚡ Muy eficiente, 1.5GB RAM
- **gemma2:2b** - 🔍 De Google, bueno para tareas específicas
- **mistral:7b** - 🧠 Excelente calidad, 4GB RAM

### 2. **Google Gemini API - Gratis con límites**

#### Configuración:
1. Ve a [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Crea una API key gratuita
3. Añade a `.streamlit/secrets.toml`:
```toml
GOOGLE_API_KEY = "tu-api-key-aqui"
```

#### Límites Gratuitos:
- **15 requests por minuto**
- **1,500 requests por día**
- Modelos disponibles: `gemini-1.5-flash`, `gemini-1.5-pro`

### 3. **Hugging Face Inference API - 30,000 requests/mes gratis**

#### Configuración:
1. Ve a [Hugging Face](https://huggingface.co/settings/tokens)
2. Crea un token de acceso
3. Añade a `.streamlit/secrets.toml`:
```toml
HUGGINGFACE_API_KEY = "tu-token-aqui"
```

#### Modelos Recomendados:
- `microsoft/DialoGPT-medium` - Chat en español
- `microsoft/DialoGPT-large` - Chat avanzado
- `gpt2` - Texto en inglés
- `facebook/opt-350m` - Texto multilingüe

### 4. **Together AI - $25 créditos gratis mensuales**

#### Configuración:
1. Ve a [Together AI](https://together.ai/)
2. Regístrate y obtén $25 créditos gratis
3. Crea una API key
4. Añade a `.streamlit/secrets.toml`:
```toml
TOGETHER_API_KEY = "tu-api-key-aqui"
```

#### Modelos Recomendados:
- `togethercomputer/llama-2-7b-chat` - Chat de alta calidad
- `togethercomputer/llama-2-13b-chat` - Chat avanzado
- `togethercomputer/falcon-7b-instruct` - Instrucciones
- `togethercomputer/redpajama-incite-7b-instruct` - Instrucciones

## 📊 Comparación de Modelos

| Modelo | Tipo | Velocidad | Calidad | RAM | Gratis |
|--------|------|-----------|---------|-----|--------|
| llama3.2:1b | Local | ⚡⚡⚡ | ⭐⭐ | 1GB | ✅ |
| llama3.2:3b | Local | ⚡⚡ | ⭐⭐⭐ | 2GB | ✅ |
| qwen2.5:3b | Local | ⚡⚡ | ⭐⭐⭐⭐ | 2GB | ✅ |
| mistral:7b | Local | ⚡ | ⭐⭐⭐⭐⭐ | 4GB | ✅ |
| gemini-1.5-flash | API | ⚡⚡⚡ | ⭐⭐⭐⭐⭐ | - | ✅* |
| Together AI | API | ⚡⚡ | ⭐⭐⭐⭐ | - | ✅** |

*15 req/min gratis
**$25 créditos/mes gratis

## 🚀 Configuración Rápida

### Para Ollama (Recomendado):
```bash
# 1. Instalar Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 2. Iniciar servicio
ollama serve

# 3. Descargar modelo recomendado
ollama pull llama3.2:3b

# 4. Probar
ollama run llama3.2:3b "Hola, ¿cómo estás?"
```

### Para APIs:
1. Crea las API keys mencionadas arriba
2. Añádelas a `.streamlit/secrets.toml`
3. Instala dependencias adicionales:
```bash
pip install langchain-groq langchain-together
```

## 💡 Recomendaciones por Caso de Uso

### Para Investigación Académica:
- **llama3.2:3b** (local) - Buen balance
- **mistral:7b** (local) - Mejor calidad
- **gemini-1.5-flash** (API) - Excelente para análisis

### Para Chat en Español:
- **qwen2.5:3b** (local) - Especializado en español
- **llama3.2:3b** (local) - Bueno en español

### Para Uso Intensivo:
- **llama3.2:1b** (local) - Muy rápido
- **phi3:mini** (local) - Muy eficiente

### Para Máxima Calidad:
- **mistral:7b** (local) - Excelente calidad
- **gemini-1.5-flash** (API) - Muy preciso

## 🔧 Solución de Problemas

### Ollama no responde:
```bash
# Reiniciar servicio
ollama serve

# Verificar modelos instalados
ollama list

# Reinstalar modelo
ollama rm llama3.2:3b
ollama pull llama3.2:3b
```

### Error de memoria:
- Usa modelos más pequeños (1b o 2b)
- Cierra otras aplicaciones
- Aumenta la memoria virtual

### Error de API:
- Verifica que las API keys estén correctas
- Revisa los límites de uso
- Prueba con otro modelo

## 📈 Monitoreo de Uso

### Ollama:
```bash
# Ver uso de memoria
ollama ps

# Ver logs
ollama logs
```

### APIs:
- Google Gemini: [Google AI Studio](https://makersuite.google.com/app/apikey)
- Hugging Face: [Settings](https://huggingface.co/settings/tokens)
- Together AI: [Dashboard](https://together.ai/dashboard)

¡Con estos modelos tendrás acceso a LLMs de alta calidad sin costo! 🎉

