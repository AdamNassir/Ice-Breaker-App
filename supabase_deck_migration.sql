-- Run ONCE in Supabase SQL Editor, using its SQL Editor role (postgres).
-- Existing rooms and data remain unchanged. Required for the Vercel global editor.
create table if not exists icebreaker.shared_decks (
  id integer primary key check (id = 1),
  revision text not null,
  state jsonb not null,
  updated_at timestamptz not null default now()
);
alter table icebreaker.shared_decks enable row level security;
grant select, insert, update on icebreaker.shared_decks to icebreaker_app;
drop policy if exists shared_deck_app_only on icebreaker.shared_decks;
create policy shared_deck_app_only on icebreaker.shared_decks for all to icebreaker_app
  using (true) with check (true);
