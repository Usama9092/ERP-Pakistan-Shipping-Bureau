# EPAS v3.8 — Project-Specific Left Navigation

When a user selects a project from the project register, the selected project becomes the primary navigation context. The global role workspace navigation is replaced by a project-specific left sidebar.

## Left navigation inside a selected project

1. Project Overview
2. Plan Appraisal — only when included in project scope
3. NSC Survey — only when included in project scope
4. In-Service Survey — only when included in project scope
5. Certification
6. Documents
7. Notifications
8. Audit Trail

The sidebar also shows the selected project, vessel, current phase, current survey cycle and next survey date, plus a **Change Project** control.

Role permissions and data security are still enforced by the backend. The navigation is contextual and does not grant authorization.

## Preview files

- `frontend_preview/project_navigation/project_specific_navigation.html`
- `frontend_preview/project_navigation/project_specific_navigation_preview.png`
- `frontend_preview/project_navigation/ai_reference_project_navigation.png`
