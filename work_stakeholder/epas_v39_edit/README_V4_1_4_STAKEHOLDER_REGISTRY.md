# EPAS v4.1.4 — GM Stakeholder Registry

## What changed

The **Projects** tab for GM now has two peer actions:

- **+ Create Project**
- **+ New Stakeholder**

`+ New Stakeholder` opens a dedicated GM-only page where the GM can register a reusable:

- Owner
- Designer
- Ship Management
- Shipyard

The new stakeholder is persisted in Supabase in `stakeholder_registry` in production, and in the demo in-memory store when the app is running in demo mode.

## Project creation

The GM Project Creation form no longer accepts free-text stakeholder company names for the four external stakeholder roles. Instead it loads active registry records and lets the GM select:

- Owner
- Designer
- Ship Management
- Shipyard

The project creation RPC copies the selected registry record into the project-scoped `stakeholders` snapshot and stores `registry_id` for lineage.

Phase rules:

- Plan Appraisal selected → Designer required
- NSC Survey selected → Shipyard required
- In-Service selected → Owner required
- In-Service selected → Ship Management required

## Production migration

Apply after the existing production migrations:

`database/production_v4_1_4_stakeholder_registry.sql`

The migration creates:

- `stakeholder_registry`
- registry RLS/policies
- GM-only `epas_create_stakeholder(...)`
- `epas_list_stakeholder_registry(...)`
- project stakeholder `registry_id` linkage
- project snapshot fields
- updated `epas_create_project(...)`

## Demo mode

The demo contains four sample stakeholder companies and supports creating additional demo stakeholders from the new GM page. Nothing is written to Supabase in demo mode.


## UI placement

In **Projects**, GM sees two peer actions: **Create Project** and **Create New Stakeholder**. The stakeholder page is not part of the selected-project navigation and is intentionally kept at the project-register level. Other roles cannot access it.
