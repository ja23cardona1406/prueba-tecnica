from typing import Any

from ..core.config import Settings


class StripeConfigurationError(RuntimeError):
    pass


class StripeCheckoutError(RuntimeError):
    pass


def create_checkout_session(
    settings: Settings,
    product: dict,
    quantity: int,
    customer_email: str | None = None,
) -> dict[str, Any]:
    if not settings.is_stripe_configured:
        raise StripeConfigurationError("Stripe is not configured")

    try:
        import stripe
    except ImportError as exc:
        raise StripeConfigurationError("Stripe package is not installed") from exc

    stripe.api_key = settings.stripe_secret_key
    stripe.api_version = "2026-02-25.clover"

    if settings.stripe_price_id:
        line_item = {"price": settings.stripe_price_id, "quantity": quantity}
    else:
        line_item = {
            "quantity": quantity,
            "price_data": {
                "currency": (product.get("currency") or "COP").lower(),
                "unit_amount": int(product["price_cop"]),
                "product_data": {
                    "name": product["name"],
                    "description": product.get("description") or "Bertolli Pro 900",
                },
            },
        }

    try:
        session = stripe.checkout.Session.create(
            mode="payment",
            line_items=[line_item],
            success_url=settings.stripe_success_url,
            cancel_url=settings.stripe_cancel_url,
            customer_email=customer_email or None,
            metadata={
                "product_id": product["id"],
                "quantity": str(quantity),
            },
        )
    except Exception as exc:
        raise StripeCheckoutError("Could not create Stripe Checkout Session") from exc

    return {
        "success": True,
        "url": session.url,
        "session_id": session.id,
        "source": "stripe",
    }
