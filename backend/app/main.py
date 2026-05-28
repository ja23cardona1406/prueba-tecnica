from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import get_settings
from .routers import assistant, checkout, health, leads, orders, products, rag


settings = get_settings()

app = FastAPI(
    title="Bertolli Pro 900 Backend",
    description="Progressive backend for leads, products, orders, checkout, and assistant chat.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(health.router)
app.include_router(health.router, prefix="/api")
app.include_router(leads.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
app.include_router(checkout.router, prefix="/api")
app.include_router(assistant.router, prefix="/api")
app.include_router(rag.router, prefix="/api")


@app.get("/")
def root():
    return {
        "service": "bertolli-pro-900-backend",
        "status": "ok",
        "docs": "/docs",
        "health": "/health",
    }
