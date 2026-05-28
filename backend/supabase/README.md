# Supabase setup

Estos scripts preparan la persistencia opcional para la landing Bertolli Pro 900.

## Orden recomendado

1. Ejecutar `schema.sql` en el SQL editor de Supabase.
2. Ejecutar `vector_schema.sql` para crear las tablas RAG y la funcion `match_rag_chunks`.
3. Ejecutar `policies.sql` para activar RLS y politicas minimas.
4. Ejecutar `seed.sql` para cargar el producto base.

## Tablas

- `leads`: solicitudes del formulario.
- `products`: catalogo de productos activos.
- `orders`: ordenes locales y sesiones de Stripe Checkout.
- `assistant_messages`: historial basico del asistente.
- `rag_documents`: documentos cargados para RAG.
- `rag_chunks`: fragmentos con embeddings `vector(384)`.

## Seguridad

El backend usa `SUPABASE_SERVICE_ROLE_KEY` desde `backend/.env`. Esa key no necesita politicas publicas porque bypasses RLS y nunca debe llegar al navegador.

La politica publica de `leads` permite insert con anon key solo si en el futuro se decide permitir escritura directa desde frontend. Esta version prioriza que el frontend hable con el backend.

No se crean politicas publicas de lectura para `leads`, `products`, `orders`, `assistant_messages`, `rag_documents` ni `rag_chunks`; las lecturas publicas pasan por el backend.
