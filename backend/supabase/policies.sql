alter table public.leads enable row level security;
alter table public.products enable row level security;
alter table public.orders enable row level security;
alter table public.assistant_messages enable row level security;
alter table public.rag_documents enable row level security;
alter table public.rag_chunks enable row level security;

drop policy if exists "Allow public lead inserts" on public.leads;
create policy "Allow public lead inserts"
on public.leads
for insert
to anon
with check (true);

-- No public read policies are created for leads, orders, products,
-- assistant_messages, rag_documents, or rag_chunks.
-- The backend uses SUPABASE_SERVICE_ROLE_KEY, which bypasses RLS server-side.
-- Keep that key only in backend/.env and never expose it to browser code.
