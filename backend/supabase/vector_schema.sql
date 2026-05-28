create extension if not exists vector with schema extensions;

create table if not exists public.rag_documents (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  source text default 'manual',
  metadata jsonb default '{}'::jsonb,
  created_at timestamptz default now()
);

create table if not exists public.rag_chunks (
  id uuid primary key default gen_random_uuid(),
  document_id uuid not null references public.rag_documents(id) on delete cascade,
  chunk_index integer not null,
  content text not null,
  embedding vector(384) not null,
  token_count integer,
  metadata jsonb default '{}'::jsonb,
  created_at timestamptz default now()
);

create index if not exists idx_rag_chunks_document_id
on public.rag_chunks(document_id);

create index if not exists idx_rag_chunks_embedding
on public.rag_chunks
using hnsw (embedding vector_cosine_ops);

create or replace function public.match_rag_chunks(
  query_embedding vector(384),
  match_count int default 5,
  match_threshold float default 0.68
)
returns table (
  id uuid,
  document_id uuid,
  chunk_index integer,
  content text,
  metadata jsonb,
  similarity float,
  document_title text,
  document_source text
)
language sql
stable
as $$
  select
    c.id,
    c.document_id,
    c.chunk_index,
    c.content,
    c.metadata,
    1 - (c.embedding <=> query_embedding) as similarity,
    d.title as document_title,
    d.source as document_source
  from public.rag_chunks c
  join public.rag_documents d on d.id = c.document_id
  where 1 - (c.embedding <=> query_embedding) >= match_threshold
  order by c.embedding <=> query_embedding
  limit match_count;
$$;
