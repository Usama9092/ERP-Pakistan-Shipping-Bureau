-- EPAS v4.1.4 · project-scoped Plan Appraisal visibility
-- All active members of the selected project may read its controlled appraisal
-- artifacts. Creation remains restricted to the security-definer workflow RPC.

begin;

alter table if exists public.plan_appraisal_artifacts enable row level security;

drop policy if exists plan_appraisal_artifacts_select_v21
  on public.plan_appraisal_artifacts;
drop policy if exists plan_appraisal_artifacts_project_member_select_v414
  on public.plan_appraisal_artifacts;

create policy plan_appraisal_artifacts_project_member_select_v414
on public.plan_appraisal_artifacts
for select
to authenticated
using (
  exists (
    select 1
    from public.project_members pm
    where pm.project_id = plan_appraisal_artifacts.project_id
      and pm.user_id = auth.uid()
      and pm.active
  )
);

revoke insert, update, delete on public.plan_appraisal_artifacts
from anon, authenticated;

commit;

