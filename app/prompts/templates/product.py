# app/prompts/templates/product.py
from app.prompts.base import PromptTemplate


PRODUCT_DESCRIPTION = PromptTemplate(
    name="product_description",
    system_message="Eres un experto copywriter de ecommerce. Escribes descripciones persuasivas, claras y SEO-optimizadas que convierten visitantes en clientes.",
    template="""Crea una descripción completa de producto para ecommerce.

**Información del producto:**
- Nombre: {product_name}
- Categoría: {category}
- Características: {features}
- Precio: {price}€

**Público objetivo:** {target_audience}
**Tono deseado:** {tone}

**Contexto de la marca:**
{brand_context}

**Genera lo siguiente:**

1. **Título SEO** (máximo 60 caracteres)
2. **Descripción corta** (160 caracteres para meta description)
3. **Descripción detallada** (200-300 palabras):
   - Hook inicial que capte atención
   - Beneficios clave (no solo características)
   - Uso/aplicación del producto
   - Call to action

4. **Beneficios en bullets** (3-5 puntos concisos)

5. **Keywords SEO** (5-7 keywords relevantes)

Formato: Markdown claro y estructurado.""",
    variables=["product_name", "category", "features", "price", "target_audience", "tone", "brand_context"],
    temperature=0.8,
    max_tokens=1500
)


PRODUCT_CATEGORIZATION = PromptTemplate(
    name="product_categorization",
    system_message="Eres un experto en taxonomías de ecommerce y clasificación de productos.",
    template="""Analiza este producto y asígnale la categoría correcta basándote en el catálogo existente.

**Producto:**
- Nombre: {product_name}
- Descripción: {description}

**Categorías disponibles en el catálogo:**
{categories}

**Contexto del catálogo:**
{catalog_context}

**Responde SOLO con un JSON válido:**
{{
  "main_category": "...",
  "subcategory": "...",
  "tags": ["...", "...", "..."],
  "confidence": 0.95,
  "reasoning": "breve explicación"
}}""",
    variables=["product_name", "description", "categories", "catalog_context"],
    temperature=0.3,
    max_tokens=500
)


META_TAGS_GENERATOR = PromptTemplate(
    name="meta_tags_generator",
    system_message="Eres un especialista en SEO para ecommerce.",
    template="""Genera meta tags optimizados para este producto.

**Producto:**
{product_name}

**Descripción breve:**
{short_description}

**Keywords objetivo:**
{target_keywords}

**Genera:**

1. **Title tag** (50-60 caracteres)
   - Incluye palabra clave principal
   - Incluye marca si es relevante
   - Persuasivo y clicable

2. **Meta description** (150-160 caracteres)
   - Describe beneficio principal
   - Incluye call to action
   - Keywords naturalmente integradas

3. **Keywords meta tag** (5-10 keywords separadas por comas)

4. **Open Graph tags** (para redes sociales)
   - og:title
   - og:description

Formato: JSON estructurado""",
    variables=["product_name", "short_description", "target_keywords"],
    temperature=0.7,
    max_tokens=800
)