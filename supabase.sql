-- Run once in the Supabase SQL Editor as postgres.
-- FIRST replace the placeholder with a strong password (escape any single quotes).
-- This role is deliberately separate from the Supabase anon/authenticated roles.
create role icebreaker_app login password 'password';
create schema if not exists icebreaker;
revoke all on schema icebreaker from public, anon, authenticated;
create table if not exists icebreaker.rooms (
  code text primary key,
  expires_at double precision not null,
  state jsonb not null
);
create index if not exists rooms_expiry on icebreaker.rooms(expires_at);
alter table icebreaker.rooms enable row level security;
grant usage on schema icebreaker to icebreaker_app;
grant select, insert, update, delete on icebreaker.rooms to icebreaker_app;
create policy app_only on icebreaker.rooms for all to icebreaker_app
  using (true) with check (true);
-- Do not add the icebreaker schema to the Supabase Data API exposed schemas.
-- To clear expired sessions periodically, run this in the SQL Editor:
-- delete from icebreaker.rooms where expires_at < extract(epoch from now());
