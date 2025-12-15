# app/services/billing_service.py
import stripe
from app.services.usage_tracking import UsageTrackingService

stripe.api_key = settings.STRIPE_SECRET_KEY

class BillingService:
    async def create_checkout_session(
        self,
        user_id: str,
        tier: str  # "starter", "pro", "business"
    ) -> str:
        """Crea sesión de pago en Stripe"""
        
        prices = {
            "starter": "price_xxx",  # ID de Stripe
            "pro": "price_yyy",
            "business": "price_zzz"
        }
        
        session = stripe.checkout.Session.create(
            customer_email=user.email,
            payment_method_types=["card"],
            line_items=[{
                "price": prices[tier],
                "quantity": 1
            }],
            mode="subscription",
            success_url=f"{settings.FRONTEND_URL}/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.FRONTEND_URL}/pricing",
            metadata={"user_id": user_id, "tier": tier}
        )
        
        return session.url
    
    async def handle_webhook(self, payload: bytes, sig_header: str):
        """Maneja webhooks de Stripe (subscriptions creadas, canceladas, etc.)"""
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        
        if event.type == "checkout.session.completed":
            session = event.data.object
            await self._activate_subscription(session)
        
        elif event.type == "customer.subscription.deleted":
            subscription = event.data.object
            await self._deactivate_subscription(subscription)