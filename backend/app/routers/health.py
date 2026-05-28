from fastapi import APIRouter

from ..services.supabase_service import diagnose_supabase


router = APIRouter(tags=["health"])


@router.get("/health")
def health_check():
    return {"status": "ok", "service": "bertolli-backend"}


@router.get("/health/supabase")
def supabase_health_check():
    return diagnose_supabase()
