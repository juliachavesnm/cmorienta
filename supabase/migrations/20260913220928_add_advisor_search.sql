create or replace function search_advisors(search_query text)
returns setof public.advisors
language sql
stable
as $$
  select *
  from public.advisors
  where
    name ilike '%' || search_query || '%'
    or description ilike '%' || search_query || '%'
    or university ilike '%' || search_query || '%'
    or department ilike '%' || search_query || '%'
    or exists (
      select 1
      from unnest(keywords) as keyword
      where keyword ilike '%' || search_query || '%'
    );
$$;
