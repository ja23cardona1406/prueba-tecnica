from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator

from ..services.supabase_service import get_supabase_client
from .products import get_product_for_server


router = APIRouter(prefix="/orders", tags=["orders"])


class OrderRequest(BaseModel):
    product_id: str = Field(..., min_length=3, max_length=80)
    customer_name: str = Field(..., min_length=2, max_length=120)
    customer_email: str = Field(..., min_length=5, max_length=254)
    quantity: int = Field(1, ge=1, le=20)

    @field_validator("customer_email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        cleaned = value.strip()
        if "@" not in cleaned or "." not in cleaned.rsplit("@", 1)[-1]:
            raise ValueError("Invalid email address")
        return cleaned

    @field_validator("product_id", "customer_name")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()


class OrderResponse(BaseModel):
    success: bool
    source: str
    order: dict


def build_order(payload: OrderRequest, product: dict) -> dict:
    return {
        "product_id": product["id"],
        "customer_name": payload.customer_name,
        "customer_email": payload.customer_email,
        "quantity": payload.quantity,
        "amount_cop": int(product["price_cop"]) * payload.quantity,
        "status": "pending",
    }


@router.post("", response_model=OrderResponse)
def create_order(payload: OrderRequest):
    product = get_product_for_server(payload.product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    order = build_order(payload, product)
    supabase = get_supabase_client()

    if supabase is not None:
        try:
            result = supabase.table("orders").insert(order).execute()
            created = result.data[0] if result.data else order
            return {"success": True, "source": "supabase", "order": created}
        except Exception:
            pass

    local_order = {"id": f"local-{uuid4()}", **order}
    return {"success": True, "source": "local-fallback", "order": local_order}
