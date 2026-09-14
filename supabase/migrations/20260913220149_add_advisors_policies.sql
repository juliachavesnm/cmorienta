create policy "Allow public insert on advisors"
on public.advisors
for insert
to anon
with check (true);

create policy "Allow public select on advisors"
on public.advisors
for select
to anon
using (true);