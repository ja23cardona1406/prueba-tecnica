from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..services.supabase_service import get_supabase_client


router = APIRouter(prefix="/products", tags=["products"])

FALLBACK_PRODUCT = {
    "id": "bertolli-pro-900",
    "name": "Bertolli Pro 900",
    "description": "Cocina a gas profesional de 5 hornillas, 90 cm, acero inoxidable.",
    "price_cop": 4990000,
    "currency": "COP",
    "active": True,
}


class ProductResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
    price_cop: int
    currency: str = "COP"
    active: bool = True


def normalize_product(row: dict) -> dict:
    return {
        "id": row.get("id"),
        "name": row.get("name"),
        "description": row.get("description"),
        "price_cop": int(row.get("price_cop") or 0),
        "currency": row.get("currency") or "COP",
        "active": bool(row.get("active", True)),
    }


def get_local_product(product_id: str) -> dict | None:
    if product_id == FALLBACK_PRODUCT["id"]:
        return FALLBACK_PRODUCT.copy()
    return None


def get_product_for_server(product_id: str) -> dict | None:
    supabase = get_supabase_client()
    if supabase is not None:
        try:
            result = (
                supabase.table("products")
                .select("*")
                .eq("id", product_id)
                .eq("active", True)
                .limit(1)
                .execute()
            )
            if result.data:
                return normalize_product(result.data[0])
        except Exception:
            return get_local_product(product_id)

    return get_local_product(product_id)


@router.get("", response_model=list[ProductResponse])
def list_products():
    supabase = get_supabase_client()
    if supabase is not None:
        try:
            result = supabase.table("products").select("*").eq("active", True).execute()
            if result.data:
                return [normalize_product(row) for row in result.data]
        except Exception:
            pass

    return [FALLBACK_PRODUCT.copy()]


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: str):
    product = get_product_for_server(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
