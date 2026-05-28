from fastapi import APIRouter
from pydantic import BaseModel, Field, field_validator, model_validator

from ..services.supabase_service import try_insert_variants


router = APIRouter(prefix="/leads", tags=["leads"])


class LeadRequest(BaseModel):
    name: str | None = Field(default=None, max_length=120)
    full_name: str | None = Field(default=None, max_length=120)
    email: str = Field(..., min_length=5, max_length=254)
    phone: str | None = Field(default=None, max_length=40)
    city: str | None = Field(default=None, max_length=120)
    message: str = Field(..., min_length=5, max_length=2000)

    @model_validator(mode="after")
    def validate_name(self):
        if not (self.name or self.full_name):
            raise ValueError("name or full_name is required")
        return self

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        cleaned = value.strip()
        if "@" not in cleaned or "." not in cleaned.rsplit("@", 1)[-1]:
            raise ValueError("Invalid email address")
        return cleaned

    @field_validator("name", "full_name", "phone", "city", "message")
    @classmethod
    def strip_text(cls, value: str | None) -> str | None:
        return value.strip() if value is not None else None


class LeadResponse(BaseModel):
    success: bool
    source: str
    lead: dict


@router.post("", response_model=LeadResponse)
def create_lead(payload: LeadRequest):
    full_name = payload.full_name or payload.name or ""
    lead = {
        "name": full_name,
        "full_name": full_name,
        "email": payload.email,
        "phone": payload.phone,
        "city": payload.city,
        "message": payload.message,
        "product": "Bertolli Pro 900",
        "source": "landing",
    }
    lead = {key: value for key, value in lead.items() if value not in (None, "")}

    legacy_lead = {
        "name": full_name,
        "email": payload.email,
        "message": payload.message,
        "product": "Bertolli Pro 900",
        "source": "landing",
    }
    modern_minimal_lead = {
        "full_name": full_name,
        "email": payload.email,
        "phone": payload.phone,
        "city": payload.city,
        "message": payload.message,
    }
    modern_minimal_lead = {
        key: value for key, value in modern_minimal_lead.items() if value not in (None, "")
    }

    created, error = try_insert_variants("leads", [modern_minimal_lead, lead, legacy_lead])
    if created is not None:
        return {"success": True, "source": "supabase", "lead": created}

    return {"success": True, "source": "local-fallback", "lead": lead}
