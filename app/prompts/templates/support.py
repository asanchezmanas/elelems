# app/prompts/templates/support.py
from app.prompts.base import PromptTemplate


SUPPORT_RESPONSE = PromptTemplate(
    name="support_response",
    system_message="Eres un agente de soporte profesional, empático y orientado a soluciones. Siempre priorizas la satisfacción del cliente.",
    template="""Responde a esta consulta de cliente usando la información disponible.

**Consulta del cliente:**
{customer_query}

**Información relevante de la base de conocimiento:**
{knowledge_base_context}

**Políticas aplicables:**
{applicable_policies}

**Historia previa con cliente (si existe):**
{customer_history}

**Tono:** {tone}

**Genera una respuesta que:**
- Sea empática con la situación del cliente
- Resuelva la duda de forma clara y completa
- Incluya pasos específicos si aplica
- Ofrezca alternativas cuando sea necesario
- Proporcione información de contacto adicional si es complejo
- Cierre confirmando si necesita más ayuda

Máximo 250 palabras. Estilo: {tone}""",
    variables=["customer_query", "knowledge_base_context", "applicable_policies", "customer_history", "tone"],
    temperature=0.6,
    max_tokens=800
)


FAQ_GENERATOR = PromptTemplate(
    name="faq_generator",
    system_message="Eres experto en crear FAQs claras y útiles basadas en consultas reales de clientes.",
    template="""Genera una entrada de FAQ basada en esta consulta recurrente.

**Consulta recurrente:**
{recurring_question}

**Información de políticas:**
{policy_context}

**Respuestas anteriores:**
{previous_answers}

**Genera:**

1. **Pregunta reformulada** (clara y directa, como la haría un cliente)

2. **Respuesta** (150-200 palabras):
   - Respuesta directa en primer párrafo
   - Detalles adicionales si son necesarios
   - Ejemplo práctico si aplica
   - Links a más información si es relevante

3. **Keywords** (para búsqueda interna)

Tono: {tone} (profesional pero accesible)

Formato: Markdown estructurado""",
    variables=["recurring_question", "policy_context", "previous_answers", "tone"],
    temperature=0.7,
    max_tokens=1000
)


COMPLAINT_RESPONSE = PromptTemplate(
    name="complaint_response",
    system_message="Eres experto en gestión de quejas. Tu objetivo es desescalar situaciones, mostrar empatía genuina y ofrecer soluciones concretas.",
    template="""Responde a esta queja de cliente con máxima empatía y orientación a soluciones.

**Queja del cliente:**
{complaint}

**Contexto del problema:**
{problem_context}

**Políticas de resolución:**
{resolution_policies}

**Soluciones disponibles:**
{available_solutions}

**Genera respuesta que:**
1. Reconozca el problema y valide sentimientos
2. Se disculpe sinceramente (sin excusas)
3. Explique qué pasó (breve, sin culpar)
4. Ofrezca solución concreta INMEDIATA
5. Proponga compensación si aplica
6. Garantice seguimiento
7. Agradezca paciencia

**CRÍTICO:**
- NO usar frases genéricas ("lamentamos las molestias")
- SÍ ser específico y humano
- Mostrar que entendiste el problema específico

Tono: Empático, profesional, orientado a solución

Máximo 200 palabras""",
    variables=["complaint", "problem_context", "resolution_policies", "available_solutions"],
    temperature=0.7,
    max_tokens=800
)