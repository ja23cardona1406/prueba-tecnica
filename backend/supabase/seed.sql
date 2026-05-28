insert into public.products (
  id,
  name,
  description,
  price_cop,
  currency,
  active
) values (
  'bertolli-pro-900',
  'Bertolli Pro 900',
  'Cocina a gas profesional de 5 hornillas, 90 cm, acero inoxidable.',
  4990000,
  'COP',
  true
)
on conflict (id) do update set
  name = excluded.name,
  description = excluded.description,
  price_cop = excluded.price_cop,
  currency = excluded.currency,
  active = excluded.active;

insert into public.rag_documents (
  id,
  title,
  source,
  metadata
) values
(
  '11111111-1111-1111-1111-111111111111',
  'Ficha comercial Bertolli Pro 900',
  'seed',
  '{
    "product_id": "bertolli-pro-900",
    "content": "La Bertolli Pro 900 es una cocina a gas profesional de 90 cm con 5 hornillas, incluyendo quemador triple corona. Tiene cubierta en acero inoxidable cepillado, parrillas de hierro fundido, perillas metalicas y horno amplio con doble vidrio templado. Su precio referencial de lanzamiento es $4.990.000 COP."
  }'::jsonb
),
(
  '22222222-2222-2222-2222-222222222222',
  'Instalacion, gas y seguridad',
  'seed',
  '{
    "product_id": "bertolli-pro-900",
    "content": "La Bertolli Pro 900 puede configurarse para gas natural o GLP con kit de conversion. La instalacion debe realizarla un tecnico certificado, validando ventilacion, presion de gas, espacio disponible de 90 cm y conexion segun la norma local. La conversion de gas no debe hacerse de forma casera."
  }'::jsonb
),
(
  '33333333-3333-3333-3333-333333333333',
  'Garantia, limpieza y beneficios',
  'seed',
  '{
    "product_id": "bertolli-pro-900",
    "content": "La garantia contemplada para la Bertolli Pro 900 es de 24 meses limitada por defectos de fabricacion, sujeta a instalacion correcta. Para limpieza se recomienda pano suave, agua tibia y jabon neutro, evitando fibras abrasivas sobre el acero inoxidable. Sus beneficios principales son mayor superficie de trabajo, llama potente para sellar, estabilidad con ollas pesadas, horno amplio y acabado premium."
  }'::jsonb
)
on conflict (id) do update set
  title = excluded.title,
  source = excluded.source,
  metadata = excluded.metadata;

-- RAG chunks are generated later through POST /api/rag/ingest-seed so the
-- backend creates embeddings with sentence-transformers/all-MiniLM-L6-v2.
