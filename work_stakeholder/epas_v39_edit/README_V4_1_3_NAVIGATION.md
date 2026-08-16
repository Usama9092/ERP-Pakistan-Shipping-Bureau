# EPAS v4.1.3 — Fixed Sidebar Navigation

## Navigation behavior

- Global navigation is vertical and rendered in the fixed left sidebar before a project is selected.
- Once a project is selected, the global navigation is replaced by project-specific navigation.
- The project sidebar contains only workflow navigation controls; project information cards are deliberately not shown in the sidebar.
- Project phases are shown only when they are part of the selected project scope.
- Change Project appears immediately before Sign out.
- Sign out is always the final sidebar action.
- The sidebar does not horizontally scroll; long labels are clipped with ellipsis and the sidebar itself scrolls vertically when needed.

## Project navigation

Project Overview → Plan Appraisal (if applicable) → NSC Survey (if applicable) → In-Service Survey (if applicable) → Survey Status → Risk Register → Ship Register → Certification → Documents → Notifications → Audit Trail.

## No project information in the navigation area

Project code, vessel name, project summary, current cycle and next survey are intentionally not rendered inside the sidebar navigation. They remain available in the main project workspace where they belong.
