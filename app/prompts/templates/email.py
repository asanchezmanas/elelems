# app/prompts/templates/email.py
from app.prompts.base import PromptTemplate


EMAIL_ORDER_CONFIRMATION = PromptTemplate(
    name="email_order_confirmation",
    system_message="Eres un asistente de ecommerce que escribe emails transaccionales claros, amigables y profesionales.",
    template="""Genera un email de confirmación de pedido.

**Datos del pedido:**
- Número de pedido: {order_number}
- Cliente: {customer_name}
- Productos: {products}
- Total: {total}€
- Fecha estimada de entrega: {delivery_date}

**Políticas relevantes de la tienda:**
{store_policies}

**Tono:** {tone}

**El email debe incluir:**
1. Asunto atractivo y claro
2. Saludo personalizado
3. Confirmación clara del pedido
4. Resumen de productos
5. Total y método de pago
6. Información de envío y seguimiento
7. Siguientes pasos
8. Datos de contacto para dudas
9. Despedida cálida

Formato: HTML simple y responsive (sin estilos inline complejos)""",
    variables=["order_number", "customer_name", "products", "total", "delivery_date", "store_policies", "tone"],
    temperature=0.7,
    max_tokens=1200
)


EMAIL_SHIPPING_NOTIFICATION = PromptTemplate(
    name="email_shipping_notification",
    system_message="Escribes notificaciones de envío que generan confianza y anticipación.",
    template="""Genera email de notificación de envío.

**Datos:**
- Cliente: {customer_name}
- Pedido: {order_number}
- Transportista: {carrier}
- Tracking: {tracking_number}
- Estimación llegada: {estimated_delivery}

**Políticas de envío:**
{shipping_policies}

**Incluir:**
1. Asunto con sensación de progreso ("¡Tu pedido está en camino!")
2. Confirmación de envío
3. Link de tracking prominente
4. Estimación de entrega
5. Qué hacer si hay problemas
6. Preparación para la recepción

Formato: HTML simple""",
    variables=["customer_name", "order_number", "carrier", "tracking_number", "estimated_delivery", "shipping_policies"],
    temperature=0.7,
    max_tokens=1000
)


EMAIL_ABANDONED_CART = PromptTemplate(
    name="email_abandoned_cart",
    system_message="Eres experto en recuperar carritos abandonados con emails persuasivos pero no agresivos.",
    template="""Genera email para recuperar carrito abandonado.

**Datos:**
- Cliente: {customer_name}
- Productos en carrito: {cart_items}
- Valor total: {cart_value}€
- Tiempo desde abandono: {time_since_abandonment}

**Incentivos disponibles:**
{available_incentives}

**Contexto de marca:**
{brand_context}

**Tono:** {tone} (nunca agresivo)

**Estrategia:**
1. Asunto que genere curiosidad (no "¡Olvidaste algo!")
2. Recordatorio amable
3. Mostrar productos con imágenes (mencionar, no generar HTML completo)
4. Beneficio de completar compra
5. Incentivo si aplica
6. CTA claro
7. Sentido de urgencia suave (stock limitado, oferta temporal)

Formato: HTML simple""",
    variables=["customer_name", "cart_items", "cart_value", "time_since_abandonment", "available_incentives", "brand_context", "tone"],
    temperature=0.8,
    max_tokens=1200
)


