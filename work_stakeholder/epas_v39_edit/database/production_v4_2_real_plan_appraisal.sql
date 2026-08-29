-- EPAS v4.2 · Real Plan Appraisal workspace
-- Apply after production_v4_1_4_project_plan_appraisal.sql and production_v2_1_engineer_surveyor_completion.sql.
-- No seed/demo rows. This migration exposes only persisted project data and binds
-- engineer artifacts to the exact current plan revision.

begin;

-- Keep the artifact vocabulary aligned with the production v2.1 RPC.
-- Existing deployments may contain legacy lowercase values from pre-v2.1 UI code.
update plan_appraisal_artifacts
set artifact_type = case artifact_type
  when 'appraised_drawing' then 'MARKED_UP_DRAWING'
  when 'appraisal_report' then 'APPRAISAL_REPORT'
  else artifact_type
end
where artifact_type in ('appraised_drawing','appraisal_report');

-- One project-scoped read model for the master register. RLS remains authoritative.
create or replace function epas_plan_appraisal_register_v42(p_project_id uuid)
returns table(
  drawing_id uuid,
  project_id uuid,
  document_id uuid,
  drawing_no text,
  title text,
  discipline text,
  status text,
  current_revision integer,
  current_file_name text,
  designer_id uuid,
  designer_name text,
  manager_id uuid,
  manager_name text,
  engineer_id uuid,
  engineer_name text,
  submitted_at timestamptz,
  updated_at timestamptz,
  due_at timestamptz,
  open_remarks bigint,
  revision_count bigint,
  appraisal_file_count bigint
)
language sql security definer set search_path=public stable as $$
  select
    d.id,d.project_id,d.document_id,d.drawing_no,d.title,d.discipline,d.status,
    d.current_revision,d.current_file_name,d.designer_id,pd.full_name,
    d.manager_id,pm.full_name,d.engineer_id,pe.full_name,
    d.submitted_at,d.updated_at,d.due_at,
    (select count(*) from plan_appraisal_observations o where o.drawing_id=d.id and o.status='open'),
    (select count(*) from plan_revisions r where r.drawing_id=d.id),
    (select count(*) from plan_appraisal_artifacts a where a.drawing_id=d.id)
  from plan_drawings d
  left join profiles pd on pd.id=d.designer_id
  left join profiles pm on pm.id=d.manager_id
  left join profiles pe on pe.id=d.engineer_id
  where d.project_id=p_project_id
    and epas_is_project_member(p_project_id)
  order by d.discipline,d.drawing_no,d.updated_at desc;
$$;
grant execute on function epas_plan_appraisal_register_v42(uuid) to authenticated;

-- Exact revision package: designer source file + engineer outputs for THAT revision.
create or replace function epas_plan_revision_package_v42(p_drawing_id uuid)
returns table(
  revision_id uuid,
  revision_no integer,
  revision_status text,
  designer_file_name text,
  designer_storage_path text,
  designer_sha256 text,
  designer_mime_type text,
  designer_size_bytes bigint,
  submitted_by uuid,
  submitted_by_name text,
  submission_note text,
  submitted_at timestamptz,
  artifact_id uuid,
  artifact_type text,
  artifact_status text,
  artifact_file_name text,
  artifact_storage_path text,
  artifact_sha256 text,
  artifact_size_bytes bigint,
  artifact_uploaded_by uuid,
  artifact_uploaded_by_name text,
  artifact_uploaded_at timestamptz
)
language sql security definer set search_path=public stable as $$
  select
    r.id,r.revision_no,r.status,r.file_name,r.storage_path,r.sha256,r.mime_type,r.file_size_bytes,
    r.submitted_by,ps.full_name,r.submission_note,r.submitted_at,
    a.id,a.artifact_type,a.status,a.file_name,a.storage_path,a.sha256,a.size_bytes,
    a.uploaded_by,pa.full_name,a.uploaded_at
  from plan_revisions r
  join plan_drawings d on d.id=r.drawing_id
  left join profiles ps on ps.id=r.submitted_by
  left join plan_appraisal_artifacts a on a.revision_id=r.id
  left join profiles pa on pa.id=a.uploaded_by
  where r.drawing_id=p_drawing_id
    and epas_is_project_member(d.project_id)
  order by r.revision_no desc,a.uploaded_at desc nulls last;
$$;
grant execute on function epas_plan_revision_package_v42(uuid) to authenticated;

-- Internal project users need controlled artifact reads; Designer can see only
-- its own drawing's artifacts once the workflow has produced them.
drop policy if exists plan_appraisal_artifacts_project_member_select_v414 on plan_appraisal_artifacts;
drop policy if exists plan_appraisal_artifacts_select_v42 on plan_appraisal_artifacts;
create policy plan_appraisal_artifacts_select_v42
on plan_appraisal_artifacts for select to authenticated
using (
  (epas_is_internal_role() and epas_is_project_member(project_id))
  or exists(
    select 1 from plan_drawings d
    where d.id=plan_appraisal_artifacts.drawing_id
      and d.designer_id=auth.uid()
      and epas_is_project_member(d.project_id)
  )
);

-- Prevent duplicate active artifact type for the same revision while retaining
-- superseded history.
create unique index if not exists uq_plan_artifact_active_revision_type
on plan_appraisal_artifacts(revision_id,artifact_type)
where status in ('submitted','accepted');

commit;
