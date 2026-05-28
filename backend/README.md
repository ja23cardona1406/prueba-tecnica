# Bertolli Pro 900 Backend

Optional FastAPI backend for the Bertolli Pro 900 landing page. It supports leads, products, orders, Stripe Checkout, OpenRouter assistant responses, and Supabase Vector RAG while keeping all external services optional.

## Run Locally

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Render start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## Endpoints

- `GET /health`
- `GET /api/health`
- `GET /api/health/supabase`
- `POST /api/leads`
- `GET /api/products`
- `GET /api/products/{product_id}`
- `POST /api/orders`
- `POST /api/checkout/session`
- `POST /api/assistant`
- `POST /api/rag/documents`
- `POST /api/rag/search`
- `GET /api/rag/status`
- `POST /api/rag/ingest-seed`

Useful local checks:

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/health/supabase" -Method GET
Invoke-RestMethod -Uri "http://localhost:8000/api/rag/status" -Method GET
Invoke-RestMethod -Uri "http://localhost:8000/api/rag/ingest-seed" -Method POST -ContentType "application/json" -Body '{"force": true}'
```

## Fallbacks

- Supabase missing: app starts and writes use local/non-persistent fallback where possible.
- Stripe missing: checkout returns HTTP `503` with a clear JSON error.
- OpenRouter missing: assistant returns local corpus answers.
- RAG failure: assistant continues with local Bertolli corpus context.
- Assistant responses include `saved_to_supabase` temporarily for debugging.

## Supabase SQL Order

1. `supabase/schema.sql`
2. `supabase/vector_schema.sql`
3. `supabase/policies.sql`
4. `supabase/seed.sql`

RAG production storage uses Supabase PostgreSQL with pgvector. Local ChromaDB experiments are not production dependencies.

## Environment

Copy `.env.example` to `.env` locally and fill only server-side values. Never expose service role, Stripe secret, or OpenRouter keys in frontend JavaScript.

See `.env.example` for all variables.
