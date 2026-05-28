create extension if not exists pgcrypto;

create table if not exists public.leads (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  full_name text,
  email text not null,
  phone text,
  city text,
  message text not null,
  product text default 'Bertolli Pro 900',
  source text default 'landing',
  created_at timestamptz default now()
);

alter table public.leads add column if not exists full_name text;
alter table public.leads add column if not exists phone text;
alter table public.leads add column if not exists city text;

create table if not exists public.products (
  id text primary key,
  name text not null,
  description text,
  price_cop integer not null,
  currency text default 'COP',
  active boolean default true,
  created_at timestamptz default now()
);

create table if not exists public.orders (
  id uuid primary key default gen_random_uuid(),
  product_id text references public.products(id),
  customer_name text,
  customer_email text,
  quantity integer not null default 1,
  amount_cop integer not null,
  status text default 'pending',
  stripe_session_id text,
  created_at timestamptz default now()
);

create table if not exists public.assistant_messages (
  id uuid primary key default gen_random_uuid(),
  session_id text default 'default',
  user_message text not null,
  assistant_answer text not null,
  provider text,
  model_used text,
  source text default 'backend',
  fallback_used boolean default false,
  rag_used boolean default false,
  retrieved_chunks integer default 0,
  metadata jsonb default '{}'::jsonb,
  created_at timestamptz default now()
);

alter table public.assistant_messages add column if not exists session_id text default 'default';
alter table public.assistant_messages add column if not exists fallback_used boolean default false;
alter table public.assistant_messages add column if not exists rag_used boolean default false;
alter table public.assistant_messages add column if not exists retrieved_chunks integer default 0;
alter table public.assistant_messages add column if not exists metadata jsonb default '{}'::jsonb;

create index if not exists idx_products_active on public.products(active);
create index if not exists idx_orders_product_id on public.orders(product_id);
create index if not exists idx_orders_stripe_session_id on public.orders(stripe_session_id);
create index if not exists idx_assistant_messages_created_at on public.assistant_messages(created_at);
create index if not exists idx_assistant_messages_session_id on public.assistant_messages(session_id);
