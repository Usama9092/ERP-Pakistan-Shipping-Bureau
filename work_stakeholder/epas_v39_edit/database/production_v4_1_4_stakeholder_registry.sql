-- EPAS v4.1.4
-- GM-managed reusable stakeholder registry + project selection.
-- Stakeholders: OWNER, DESIGNER, SHIP_MANAGEMENT, SHIPYARD.

begin;

create table if not exists stakeholder_registry (
    id uuid primary key default gen_random_uuid(),
    stakeholder_type text not null check (stakeholder_type in ('owner','designer','ship_management','shipyard')),
    company_name text not null,
    registration_no text,
    country text,
    address text,
    city text,
    postal_code text,
    website text,
    contact_name text,
    contact_designation text,
    contact_email text,
    contact_phone text,
    contact_mobile text,
    notes text,
    status text not null default 'active' check (status in ('active','suspended','inactive','archived')),
    created_by uuid not null references profiles(id),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create unique index if not exists ux_stakeholder_registry_active_type_name
on stakeholder_registry (stakeholder_type, lower(trim(company_name)))
where status = 'active';

create index if not exists ix_stakeholder_registry_type_status
on stakeholder_registry(stakeholder_type, status, lower(company_name));

alter table stakeholders add column if not exists registry_id uuid references stakeholder_registry(id);
alter table stakeholders add column if not exists registration_no text;
alter table stakeholders add column if not exists contact_phone text;
alter table stakeholders add column if not exists contact_designation text;
alter table stakeholders add column if not exists address text;
alter table stakeholders add column if not exists status text not null default 'active';

create index if not exists ix_stakeholders_registry_id on stakeholders(registry_id);

alter table stakeholder_registry enable row level security;
alter table stakeholder_registry force row level security;
alter table stakeholders enable row level security;

-- GM can manage the reusable directory; other roles can only see active entries
-- when they are already linked to a project via copied project stakeholder rows.
drop policy if exists stakeholder_registry_gm_all on stakeholder_registry;
create policy stakeholder_registry_gm_all on stakeholder_registry
for all to authenticated
using (epas_has_role('gm'))
with check (epas_has_role('gm'));

drop policy if exists stakeholder_registry_read_active on stakeholder_registry;
create policy stakeholder_registry_read_active on stakeholder_registry
for select to authenticated
using (
    status = 'active'
    and exists (
        select 1 from stakeholders s
        join project_members pm on pm.project_id = s.project_id and pm.active = true and pm.user_id = auth.uid()
        where s.registry_id = stakeholder_registry.id
    )
);

-- GM-only creation.
create or replace function epas_create_stakeholder(
    p_stakeholder_type text,
    p_company_name text,
    p_registration_no text default null,
    p_country text default null,
    p_address text default null,
    p_city text default null,
    p_postal_code text default null,
    p_website text default null,
    p_contact_name text default null,
    p_contact_designation text default null,
    p_contact_email text default null,
    p_contact_phone text default null,
    p_contact_mobile text default null,
    p_notes text default null
) returns jsonb
language plpgsql
security definer
set search_path=public
as $$
declare
    v_row stakeholder_registry;
begin
    if not epas_has_role('gm') then
        raise exception 'Only GM Classification may create stakeholders';
    end if;
    if p_stakeholder_type not in ('owner','designer','ship_management','shipyard') then
        raise exception 'Invalid stakeholder type';
    end if;
    if coalesce(trim(p_company_name),'') = '' then
        raise exception 'Company name is required';
    end if;
    insert into stakeholder_registry(
        stakeholder_type,company_name,registration_no,country,address,city,postal_code,website,
        contact_name,contact_designation,contact_email,contact_phone,contact_mobile,notes,created_by
    ) values (
        lower(p_stakeholder_type),trim(p_company_name),nullif(trim(p_registration_no),''),nullif(trim(p_country),''),
        nullif(trim(p_address),''),nullif(trim(p_city),''),nullif(trim(p_postal_code),''),nullif(trim(p_website),''),
        nullif(trim(p_contact_name),''),nullif(trim(p_contact_designation),''),nullif(trim(p_contact_email),''),
        nullif(trim(p_contact_phone),''),nullif(trim(p_contact_mobile),''),nullif(trim(p_notes),''),auth.uid()
    ) returning * into v_row;
    return to_jsonb(v_row);
exception when unique_violation then
    raise exception 'An active stakeholder with this type and company name already exists';
end;
$$;

grant execute on function epas_create_stakeholder(text,text,text,text,text,text,text,text,text,text,text,text,text,text) to authenticated;

create or replace function epas_list_stakeholder_registry(p_stakeholder_type text default null)
returns setof stakeholder_registry
language sql
security definer
set search_path=public
as $$
    select sr.*
    from stakeholder_registry sr
    where sr.status = 'active'
      and (not epas_has_role('gm') and exists (
            select 1 from stakeholders s
            join project_members pm on pm.project_id=s.project_id and pm.active=true and pm.user_id=auth.uid()
            where s.registry_id = sr.id
      ) or epas_has_role('gm'))
      and (p_stakeholder_type is null or sr.stakeholder_type = lower(p_stakeholder_type))
    order by sr.stakeholder_type, lower(sr.company_name);
$$;

grant execute on function epas_list_stakeholder_registry(text) to authenticated;

create or replace function epas_create_project(p_payload jsonb)
returns jsonb
language plpgsql
security definer
set search_path=public
as $$
declare
  v_project projects;
  v_vessel vessels;
  v_item jsonb;
  v_code text;
  v_gm uuid := auth.uid();
  v_registry stakeholder_registry;
begin
  if not epas_has_role('gm') then raise exception 'Only GM Classification may create projects'; end if;
  if coalesce(trim(p_payload->>'name'),'') = '' then raise exception 'Project name is required'; end if;
  if coalesce(trim(p_payload->>'vessel_type'),'') = '' then raise exception 'Vessel type is required'; end if;
  if coalesce(trim(p_payload->>'flag_state'),'') = '' then raise exception 'Flag state is required'; end if;

  v_code := coalesce(nullif(trim(p_payload->>'project_code'),''), 'EPAS-' || to_char(now(),'YYYY') || '-' || lpad((extract(epoch from clock_timestamp())::bigint % 100000)::text,5,'0'));

  insert into projects(
    project_code,name,vessel_type,flag_state,phases,status,created_by,
    classification_number,register_number,contract_number,classification_request,
    classification_scope,applicable_rules,start_date,target_completion_date,
    survey_type,build_stage,remarks,activated_at,activated_by
  ) values (
    v_code,p_payload->>'name',p_payload->>'vessel_type',p_payload->>'flag_state',
    coalesce(array(select jsonb_array_elements_text(p_payload->'phases')),'{}'),
    'active',v_gm,
    p_payload->>'classification_number',p_payload->>'register_number',p_payload->>'contract_number',p_payload->>'classification_request',
    p_payload->>'classification_scope',coalesce(array(select jsonb_array_elements_text(p_payload->'applicable_rules')),'{}'),
    nullif(p_payload->>'start_date','')::date,nullif(p_payload->>'target_completion_date','')::date,
    p_payload->>'survey_type',p_payload->>'build_stage',p_payload->>'remarks',now(),v_gm
  ) returning * into v_project;

  insert into vessels(project_id,name,imo_number,flag_state,loa_m,beam_m,draft_m,power_kw,speed_knots,build_year,owner_company,current_class)
  values(v_project.id,
    coalesce(p_payload->'vessel'->>'name',v_project.name),
    nullif(p_payload->'vessel'->>'imo_number',''),v_project.flag_state,
    nullif(p_payload->'vessel'->>'loa_m','')::numeric,nullif(p_payload->'vessel'->>'beam_m','')::numeric,
    nullif(p_payload->'vessel'->>'draft_m','')::numeric,nullif(p_payload->'vessel'->>'power_kw','')::numeric,
    nullif(p_payload->'vessel'->>'speed_knots','')::numeric,nullif(p_payload->'vessel'->>'build_year','')::int,
    p_payload->'vessel'->>'owner_company','Pending Classification') returning * into v_vessel;

  insert into project_members(project_id,user_id,role,discipline) values(v_project.id,v_gm,'gm',null);

  for v_item in select * from jsonb_array_elements(coalesce(p_payload->'team','[]'::jsonb)) loop
    insert into project_members(project_id,user_id,role,discipline)
    values(v_project.id,(v_item->>'user_id')::uuid,v_item->>'role',nullif(v_item->>'discipline',''))
    on conflict do nothing;
    insert into team_assignments(project_id,user_id,role,discipline)
    values(v_project.id,(v_item->>'user_id')::uuid,v_item->>'role',nullif(v_item->>'discipline',''));
    insert into notifications(user_id,title,body,project_id,link_page,notification_type,severity,entity_type,entity_id)
    values((v_item->>'user_id')::uuid,'New project assignment','You have been assigned to project '||v_project.project_code,v_project.id,'project','assignment','info','project',v_project.id);
  end loop;

  for v_item in select * from jsonb_array_elements(coalesce(p_payload->'stakeholders','[]'::jsonb)) loop
    v_registry := null;
    if nullif(v_item->>'registry_id','') is not null then
      select * into v_registry from stakeholder_registry
      where id=(v_item->>'registry_id')::uuid and status='active';
      if v_registry.id is null then raise exception 'Selected stakeholder is not active or not found'; end if;
      if v_registry.stakeholder_type <> v_item->>'stakeholder_type' then
        raise exception 'Selected stakeholder type does not match requested project role';
      end if;
      insert into stakeholders(
        project_id,company_name,contact_name,contact_email,stakeholder_type,stakeholder_user_id,
        registry_id,registration_no,contact_phone,contact_designation,address,status
      ) values(
        v_project.id,v_registry.company_name,v_registry.contact_name,v_registry.contact_email,v_registry.stakeholder_type,nullif(v_item->>'user_id','')::uuid,
        v_registry.id,v_registry.registration_no,v_registry.contact_phone,v_registry.contact_designation,v_registry.address,'active'
      );
    elsif coalesce(trim(v_item->>'company_name'),'') <> '' then
      -- Backward-compatible legacy payload path for older saved project drafts.
      insert into stakeholders(project_id,company_name,contact_name,contact_email,stakeholder_type,stakeholder_user_id)
      values(v_project.id,v_item->>'company_name',v_item->>'contact_name',v_item->>'contact_email',v_item->>'stakeholder_type',nullif(v_item->>'user_id','')::uuid);
    end if;

    if nullif(v_item->>'user_id','') is not null then
      insert into project_members(project_id,user_id,role)
      values(v_project.id,(v_item->>'user_id')::uuid,v_item->>'stakeholder_type') on conflict do nothing;
      insert into notifications(user_id,title,body,project_id,link_page,notification_type,severity,entity_type,entity_id)
      values((v_item->>'user_id')::uuid,'Project stakeholder access', 'You have been added as a stakeholder to project '||v_project.project_code,v_project.id,'projects','assignment','info','project',v_project.id);
    end if;
    if coalesce(trim(coalesce(v_registry.contact_email,v_item->>'contact_email')),'') <> '' then
      insert into notification_outbox(project_id,recipient_email,subject,body)
      values(v_project.id,coalesce(v_registry.contact_email,v_item->>'contact_email'),'EPAS Project Assignment','You have been added as a stakeholder to project '||v_project.project_code||'. Sign in to the EPAS portal to view permitted project information.');
    end if;
  end loop;

  insert into project_milestones(project_id,code,title,phase,due_date,status,owner_id)
  select v_project.id, x.code, x.title, x.phase,
         case when v_project.target_completion_date is not null then v_project.target_completion_date else null end,
         'pending',v_gm
  from (values
    ('PA-01','Plan Appraisal Complete','plan_appraisal'),
    ('SUR-01','Survey Programme Complete','nsc_survey'),
    ('CERT-01','Certificate / Class Record','in_service')
  ) x(code,title,phase)
  where x.phase = any(v_project.phases);

  insert into workflow_events(project_id,entity_type,entity_id,event_type,to_status,actor_id,note)
  values(v_project.id,'project',v_project.id,'PROJECT_CREATED','active',v_gm,'Project created and activated by GM');

  insert into notifications(user_id,title,body,project_id,link_page,notification_type,severity,entity_type,entity_id)
  values(v_gm,'Project activated',v_project.project_code||' is active and ready for execution.',v_project.id,'projects','workflow','success','project',v_project.id);

  return jsonb_build_object('project',to_jsonb(v_project),'vessel',to_jsonb(v_vessel));
end;
$$;

grant execute on function epas_create_project(jsonb) to authenticated;

commit;
