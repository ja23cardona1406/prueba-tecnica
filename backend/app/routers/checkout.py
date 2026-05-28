from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator

from ..core.config import get_settings
from ..services.stripe_service import (
    StripeCheckoutError,
    StripeConfigurationError,
    create_checkout_session,
)
from ..services.supabase_service import get_supabase_client
from .products import get_product_for_server


router = APIRouter(prefix="/checkout", tags=["checkout"])


class CheckoutRequest(BaseModel):
    product_id: str = Field(..., min_length=3, max_length=80)
    quantity: int = Field(1, ge=1, le=20)
    customer_email: str | None = Field(default=None, max_length=254)

    @field_validator("customer_email")
    @classmethod
    def validate_email(cls, value: str | None) -> str | None:
        if value is None or not value.strip():
            return None
        cleaned = value.strip()
        if "@" not in cleaned or "." not in cleaned.rsplit("@", 1)[-1]:
            raise ValueError("Invalid email address")
        return cleaned

    @field_validator("product_id")
    @classmethod
    def strip_product_id(cls, value: str) -> str:
        return value.strip()


class CheckoutResponse(BaseModel):
    success: bool = True
    url: str
    session_id: str
    source: str = "stripe"


@router.post("/session", response_model=CheckoutResponse)
def create_session(payload: CheckoutRequest):
    settings = get_settings()
    product = get_product_for_server(payload.product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    try:
        session = create_checkout_session(
            settings=settings,
            product=product,
            quantity=payload.quantity,
            customer_email=payload.customer_email,
        )
    except StripeConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except StripeCheckoutError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    supabase = get_supabase_client()
    if supabase is not None:
        try:
            order = {
                "product_id": product["id"],
                "customer_email": payload.customer_email,
                "quantity": payload.quantity,
                "amount_cop": int(product["price_cop"]) * payload.quantity,
                "status": "checkout_created",
                "stripe_session_id": session["session_id"],
            }
            supabase.table("orders").insert(order).execute()
        except Exception:
            pass

    return session


@router.post("/create-session", response_model=CheckoutResponse, include_in_schema=False)
def create_session_legacy(payload: CheckoutRequest):
    return create_session(payload)
