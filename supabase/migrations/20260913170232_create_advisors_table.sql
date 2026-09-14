create table public.advisors (
  id uuid primary key default gen_random_uuid(),

  name text not null,
  description text,
  university text,
  department text,
  email text,
  profile_url text,
  keywords text[],

  updated_at timestamptz not null default now(),

  constraint advisors_profile_url_unique unique (profile_url)
);

alter table public.advisors enable row level security;