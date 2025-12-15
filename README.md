# elelems 

# 🛒 RAG Ecommerce - Sistema de Generación de Contenido con RAG

Sistema completo de **generación de contenido automatizada para ecommerce** usando **RAG (Retrieval-Augmented Generation)** con stack 100% gratuito hasta escala media.

## ✨ Características

- 📄 **Parsing inteligente** de documentos (PDF, DOCX, PPTX, TXT, MD, HTML) con Docling
- 🧠 **Embeddings locales** con sentence-transformers (gratis y privado)
- 🔍 **Búsqueda semántica** en documentos con pgvector
- ✨ **Prompts dinámicos** fácilmente extensibles
- 💾 **Persistencia completa** de documentos originales en Supabase Storage
- 🚀 **Generación con Groq** (gratis, 6000 req/día) o OpenAI (backup)
- 🔐 **Control total** del pipeline RAG

## 🏗️ Arquitectura

```
FastAPI (Render) 
    ↓
Groq API (LLM gratis)
    ↓
Supabase (Storage + PostgreSQL + pgvector)
    ↓
Docling + sentence-transformers (parsing + embeddings locales)
```

## 💰 Costos

| Componente | Tier Gratuito | Costo Escalado |
|------------|---------------|----------------|
| **Groq API** | 6000 req/día | Gratis |
| **Supabase** | 1GB storage + 500MB DB | $25/mes (Pro) |
| **Render** | 750h/mes | $7/mes (hobby) |
| **Embeddings** | Locales | Gratis |
| **Total** | **$0/mes** | **~$32/mes** |

Para ~1000 documentos y ~100 generaciones/día: **$0-7/mes**

## 🚀 Quickstart

### 1. Requisitos

```bash
Python 3.10+
PostgreSQL (via Supabase)
```

### 2. Clonar y configurar

```bash
git clone <repo>
cd rag-ecommerce

# Crear virtual env
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o: venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Configurar Supabase

1. Crear cuenta en [supabase.com](https://supabase.com)
2. Crear nuevo proyecto
3. Ir a **SQL Editor** y ejecutar en orden:
   ```bash
   sql/01_enable_extensions.sql
   sql/02_create_tables.sql
   sql/03_create_functions.sql
   ```

4. Crear bucket de Storage:
   - Ir a **Storage** → **Create bucket**
   - Nombre: `documents`
   - Public: **No** (privado)

5. Obtener credenciales:
   - Ir a **Settings** → **API**
   - Copiar:
     - `Project URL` → `SUPABASE_URL`
     - `anon public` key → `SUPABASE_KEY`

### 4. Configurar Groq API

1. Crear cuenta en [console.groq.com](https://console.groq.com)
2. Ir a **API Keys** → **Create API Key**
3. Copiar key → `GROQ_API_KEY`

### 5. Crear .env

```bash
cp .env.example .env
# Editar .env con tus keys
```

Ejemplo `.env`:
```bash
# Supabase
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxxxx

# Groq
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxx
GROQ_MODEL=llama-3.1-70b-versatile

# LLM Provider (groq o openai)
LLM_PROVIDER=groq

# Embeddings (modelo local)
EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2
```

### 6. Ejecutar

```bash
# Desarrollo
uvicorn app.main:app --reload

# Producción
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

API disponible en: `http://localhost:8000`
Docs interactiva: `http://localhost:8000/docs`

## 📖 Uso

### 1. Subir documentos

```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@guia_marca.pdf" \
  -F "doc_type=brand_guide" \
  -F "preserve_sections=true"
```

**Respuesta:**
```json
{
  "document_id": "uuid-xxx",
  "filename": "guia_marca.pdf",
  "doc_type": "brand_guide",
  "total_chunks": 15,
  "status": "indexed",
  "message": "Documento procesado exitosamente: 15 chunks creados"
}
```

### 2. Generar contenido con RAG

#### Descripción de producto usando guía de marca:

```bash
curl -X POST "http://localhost:8000/api/v1/generation/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt_name": "product_description",
    "variables": {
      "product_name": "Zapatillas Running Pro",
      "category": "Deportes",
      "features": "Suela de gel, transpirables, ligeras",
      "price": "89.99",
      "target_audience": "Runners amateur",
      "tone": "deportivo y motivador"
    },
    "use_rag": true,
    "doc_type_filter": "brand_guide",
    "top_k": 3
  }'
```

**Respuesta:**
```json
{
  "content": "## Zapatillas Running Pro\n\n### Dale impulso a tus carreras...",
  "prompt_name": "product_description",
  "tokens_used": 250,
  "sources": ["guia_marca.pdf"],
  "model_used": "llama-3.1-70b-versatile"
}
```

#### Respuesta de soporte consultando políticas:

```bash
curl -X POST "http://localhost:8000/api/v1/generation/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt_name": "support_response",
    "variables": {
      "customer_query": "¿Puedo devolver un producto después de 30 días?",
      "tone": "profesional y empático"
    },
    "use_rag": true,
    "doc_type_filter": "policy",
    "rag_query": "política de devoluciones plazo"
  }'
```

### 3. Búsqueda semántica

```bash
curl -X POST "http://localhost:8000/api/v1/generation/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "política de devoluciones productos defectuosos",
    "top_k": 5,
    "doc_type": "policy",
    "similarity_threshold": 0.75
  }'
```

### 4. Listar prompts disponibles

```bash
curl "http://localhost:8000/api/v1/generation/prompts"
```

**Respuesta:**
```json
{
  "prompts": [
    {
      "name": "product_description",
      "variables": ["product_name", "category", "features", "price", "target_audience", "tone"],
      "temperature": 0.8,
      "max_tokens": 1500
    },
    {
      "name": "support_response",
      "variables": ["customer_query", "tone"],
      "temperature": 0.6,
      "max_tokens": 800
    },
    ...
  ],
  "total": 8
}
```

## 🔧 Añadir Nuevos Prompts

1. Crear archivo en `app/prompts/templates/`:

```python
# app/prompts/templates/custom.py
from app.prompts.base import PromptTemplate

CUSTOM_PROMPT = PromptTemplate(
    name="mi_prompt_custom",
    system_message="Eres un experto en...",
    template="""Genera contenido sobre: {topic}
    
    Contexto: {context}
    
    Requisitos:
    - {requirement1}
    - {requirement2}
    """,
    variables=["topic", "context", "requirement1", "requirement2"],
    temperature=0.7,
    max_tokens=1000
)
```

2. Registrar en loader (`app/prompts/loader.py`):

```python
from app.prompts.templates import custom

def _load_default_prompts(self):
    # ... otros prompts ...
    self._prompts["mi_prompt_custom"] = custom.CUSTOM_PROMPT
```

3. Usar inmediatamente:

```bash
curl -X POST ".../generate" -d '{
  "prompt_name": "mi_prompt_custom",
  "variables": {...}
}'
```

## 🗄️ Gestión de Documentos

### Listar documentos

```bash
curl "http://localhost:8000/api/v1/documents/list?doc_type=policy&page=1&page_size=20"
```

### Ver documento

```bash
curl "http://localhost:8000/api/v1/documents/{document_id}"
```

### Descargar documento original

```bash
curl "http://localhost:8000/api/v1/documents/{document_id}/download"

# Retorna URL temporal (válida 1 hora)
{"download_url": "https://...", "expires_in": 3600}
```

### Eliminar documento

```bash
curl -X DELETE "http://localhost:8000/api/v1/documents/{document_id}"
```

### Estadísticas

```bash
curl "http://localhost:8000/api/v1/documents/stats/summary"
```

```json
{
  "total_documents": 50,
  "total_chunks": 750,
  "total_size_mb": 125.5,
  "avg_chunks_per_doc": 15,
  "doc_types": {
    "policy": 10,
    "brand_guide": 5,
    "faq": 15,
    "product_guide": 20
  }
}
```

## 🚢 Deploy en Render

### 1. Preparar repositorio

```bash
git init
git add .
git commit -m "Initial commit"
git push origin main
```

### 2. Crear Web Service en Render

1. Ir a [render.com](https://render.com)
2. **New** → **Web Service**
3. Conectar repositorio
4. Configurar:
   - **Name**: `rag-ecommerce`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Añadir variables de entorno (copiar de `.env`)
6. Deploy!

**Costo:** $7/mes (Hobby) o $0 con free tier (duerme después de inactividad)

## 📊 Monitoreo

### Health checks

```bash
# General
curl "http://localhost:8000/health"

# Generación
curl "http://localhost:8000/api/v1/generation/health"
```

### Logs

```python
# Configurados en app/main.py
# Nivel: INFO
# Incluyen: parsing, chunking, embedding, generación
```

## 🔐 Seguridad

### Recomendaciones producción:

1. **API Keys**: Usar variables de entorno, nunca hardcodear
2. **CORS**: Configurar `allow_origins` específicos en `app/main.py`
3. **Rate limiting**: Añadir con `slowapi`
4. **Autenticación**: Implementar JWT para endpoints sensibles
5. **HTTPS**: Render lo proporciona automáticamente

## 🧪 Testing

```bash
# Unit tests
pytest tests/test_parsing.py
pytest tests/test_rag.py

# Integration tests
pytest tests/integration/
```

## 📝 Prompts Disponibles

| Prompt | Variables | Uso |
|--------|-----------|-----|
| `product_description` | product_name, category, features, price, target_audience, tone | Descripciones de producto |
| `product_categorization` | product_name, description, categories | Clasificación automática |
| `meta_tags_generator` | product_name, short_description, target_keywords | SEO meta tags |
| `email_order_confirmation` | order_number, customer_name, products, total, delivery_date, tone | Email confirmación |
| `email_shipping_notification` | customer_name, order_number, tracking_number | Email envío |
| `email_abandoned_cart` | customer_name, cart_items, cart_value | Recuperar carritos |
| `support_response` | customer_query, tone | Respuestas soporte |
| `faq_generator` | recurring_question, tone | Generar FAQs |
| `complaint_response` | complaint | Gestión quejas |

## 🤝 Contribuir

1. Fork el proyecto
2. Crear feature branch (`git checkout -b feature/amazing`)
3. Commit cambios (`git commit -m 'Add amazing feature'`)
4. Push a branch (`git push origin feature/amazing`)
5. Abrir Pull Request

## 📄 Licencia

MIT

## 🆘 Soporte

- **Issues**: GitHub Issues
- **Docs**: `/docs` en tu instancia
- **Email**: tu@email.com

---

Hecho con ❤️ para automatizar ecommerce