# 📚 Ejemplos de Uso - RAG Ecommerce API

Este archivo contiene ejemplos prácticos de cómo usar la API.

## 1️⃣ Subir y Procesar Documentos

### Subir guía de marca
```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@docs/guia_marca.pdf" \
  -F "doc_type=brand_guide" \
  -F "preserve_sections=true"
```

### Subir política de devoluciones
```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -F "file=@docs/politica_devoluciones.docx" \
  -F "doc_type=policy"
```

### Subir FAQs
```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -F "file=@docs/faqs.txt" \
  -F "doc_type=faq"
```

## 2️⃣ Generar Contenido con RAG

### Descripción de producto (usando guía de marca)
```bash
curl -X POST "http://localhost:8000/api/v1/generation/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt_name": "product_description",
    "variables": {
      "product_name": "Zapatillas Running Pro X1",
      "category": "Calzado Deportivo",
      "features": "Suela EVA de alta densidad, upper mesh transpirable, refuerzos laterales, plantilla memory foam",
      "price": "89.99",
      "target_audience": "Runners recreativos que buscan comodidad y durabilidad",
      "tone": "deportivo, motivador y cercano"
    },
    "use_rag": true,
    "doc_type_filter": "brand_guide",
    "top_k": 3
  }'
```

### Respuesta de soporte (consultando políticas)
```bash
curl -X POST "http://localhost:8000/api/v1/generation/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt_name": "support_response",
    "variables": {
      "customer_query": "Compré unas zapatillas hace 35 días y me están doliendo los pies. ¿Puedo devolverlas aunque haya pasado el plazo de 30 días?",
      "tone": "profesional, empático y orientado a soluciones"
    },
    "use_rag": true,
    "doc_type_filter": "policy",
    "rag_query": "política de devoluciones plazo excepciones"
  }'
```

### Email de confirmación de pedido
```bash
curl -X POST "http://localhost:8000/api/v1/generation/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt_name": "email_order_confirmation",
    "variables": {
      "order_number": "ORD-2024-12345",
      "customer_name": "María González",
      "products": "1x Zapatillas Running Pro X1 (Talla 39) - €89.99\n1x Calcetines Running Pack x3 - €12.99",
      "total": "102.98",
      "delivery_date": "15-20 diciembre 2024",
      "store_policies": "Envío gratis en pedidos +€50. Devoluciones gratis hasta 30 días.",
      "tone": "amigable y profesional"
    },
    "use_rag": false
  }'
```

### Meta tags SEO
```bash
curl -X POST "http://localhost:8000/api/v1/generation/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt_name": "meta_tags_generator",
    "variables": {
      "product_name": "Zapatillas Running Pro X1",
      "short_description": "Zapatillas de running con suela EVA y upper transpirable para máxima comodidad",
      "target_keywords": "zapatillas running, calzado deportivo, running shoes, zapatillas comodas"
    },
    "use_rag": false
  }'
```

### Respuesta a queja
```bash
curl -X POST "http://localhost:8000/api/v1/generation/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt_name": "complaint_response",
    "variables": {
      "complaint": "Pedí envío express hace 5 días y aún no ha llegado. Necesito las zapatillas para una carrera este fin de semana. Muy decepcionado con el servicio.",
      "problem_context": "Pedido ORD-2024-12340, envío express contratado, transportista reporta retraso en centro logístico",
      "resolution_policies": "Reembolso de envío express si supera plazo prometido, compensación con cupón",
      "available_solutions": "Reembolso inmediato €10 del envío, cupón €20 para próxima compra, opción de cancelación y reembolso completo"
    },
    "use_rag": false
  }'
```

## 3️⃣ Búsqueda Semántica

### Buscar en documentos de políticas
```bash
curl -X POST "http://localhost:8000/api/v1/generation/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "política de devoluciones para productos defectuosos o con defecto de fábrica",
    "top_k": 5,
    "doc_type": "policy",
    "similarity_threshold": 0.75
  }'
```

### Buscar en FAQs
```bash
curl -X POST "http://localhost:8000/api/v1/generation/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "cómo rastrear mi pedido seguimiento envío",
    "top_k": 3,
    "doc_type": "faq",
    "similarity_threshold": 0.7
  }'
```

### Buscar en guías de producto
```bash
curl -X POST "http://localhost:8000/api/v1/generation/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "cómo elegir la talla correcta de zapatillas",
    "top_k": 5,
    "doc_type": "product_guide"
  }'
```

## 4️⃣ Gestión de Documentos

### Listar todos los documentos
```bash
curl "http://localhost:8000/api/v1/documents/list?page=1&page_size=20"
```

### Filtrar por tipo de documento
```bash
curl "http://localhost:8000/api/v1/documents/list?doc_type=policy&page=1"
```

### Obtener información de un documento
```bash
curl "http://localhost:8000/api/v1/documents/{document_id}"
```

### Descargar documento original
```bash
# Obtener URL temporal
curl "http://localhost:8000/api/v1/documents/{document_id}/download"

# La respuesta incluye una URL firmada válida por 1 hora
# {"download_url": "https://...", "expires_in": 3600}
```

### Eliminar documento
```bash
curl -X DELETE "http://localhost:8000/api/v1/documents/{document_id}"
```

### Ver estadísticas
```bash
curl "http://localhost:8000/api/v1/documents/stats/summary"
```

## 5️⃣ Información y Ayuda

### Listar prompts disponibles
```bash
curl "http://localhost:8000/api/v1/generation/prompts"
```

### Health checks
```bash
# General
curl "http://localhost:8000/health"

# Servicio de generación
curl "http://localhost:8000/api/v1/generation/health"
```

## 6️⃣ Workflows Completos

### Workflow: Setup inicial de base de conocimiento
```bash
# 1. Subir guía de marca
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -F "file=@guia_marca.pdf" -F "doc_type=brand_guide"

# 2. Subir políticas
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -F "file=@politica_devoluciones.pdf" -F "doc_type=policy"

curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -F "file=@politica_envios.pdf" -F "doc_type=policy"

# 3. Subir FAQs
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -F "file=@faqs.txt" -F "doc_type=faq"

# 4. Verificar indexación
curl "http://localhost:8000/api/v1/documents/stats/summary"
```

### Workflow: Crear descripción completa de producto
```bash
# 1. Generar descripción principal
curl -X POST "http://localhost:8000/api/v1/generation/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt_name": "product_description",
    "variables": {...},
    "use_rag": true,
    "doc_type_filter": "brand_guide"
  }' > descripcion.json

# 2. Generar meta tags SEO
curl -X POST "http://localhost:8000/api/v1/generation/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt_name": "meta_tags_generator",
    "variables": {...}
  }' > meta_tags.json

# 3. Categorizar producto
curl -X POST "http://localhost:8000/api/v1/generation/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt_name": "product_categorization",
    "variables": {...},
    "use_rag": true
  }' > categoria.json
```

### Workflow: Responder consulta de cliente
```bash
# 1. Buscar información relevante
curl -X POST "http://localhost:8000/api/v1/generation/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "consulta del cliente...",
    "top_k": 5,
    "doc_type": "policy"
  }' > contexto.json

# 2. Generar respuesta
curl -X POST "http://localhost:8000/api/v1/generation/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt_name": "support_response",
    "variables": {
      "customer_query": "...",
      "tone": "profesional y empático"
    },
    "use_rag": true,
    "doc_type_filter": "policy"
  }' > respuesta.json
```

## 7️⃣ Integración con Python

```python
import requests

API_URL = "http://localhost:8000/api/v1"

# Subir documento
def upload_document(file_path, doc_type):
    with open(file_path, 'rb') as f:
        response = requests.post(
            f"{API_URL}/documents/upload",
            files={"file": f},
            data={"doc_type": doc_type}
        )
    return response.json()

# Generar contenido
def generate_content(prompt_name, variables, use_rag=False):
    response = requests.post(
        f"{API_URL}/generation/generate",
        json={
            "prompt_name": prompt_name,
            "variables": variables,
            "use_rag": use_rag
        }
    )
    return response.json()

# Ejemplo de uso
result = generate_content(
    prompt_name="product_description",
    variables={
        "product_name": "Zapatillas Running Pro",
        "category": "Deportes",
        "features": "Suela de gel, transpirables",
        "price": "89.99",
        "target_audience": "Runners amateur",
        "tone": "deportivo"
    },
    use_rag=True
)

print(result['content'])
```

## 8️⃣ Tips y Mejores Prácticas

### Optimizar búsquedas RAG
- Usa `doc_type_filter` para enfocarte en documentos relevantes
- Ajusta `top_k` según contexto necesario (3-5 típicamente)
- Usa `similarity_threshold` para filtrar resultados de baja calidad

### Prompts efectivos
- Sé específico en las variables
- Usa `tone` para controlar el estilo
- En RAG, usa `rag_query` personalizado si la búsqueda debe ser diferente al contenido final

### Gestión de documentos
- Usa tipos consistentes (`brand_guide`, `policy`, `faq`, etc.)
- Actualiza documentos re-subiéndolos con el mismo nombre
- Revisa estadísticas regularmente para mantener base de conocimiento limpia