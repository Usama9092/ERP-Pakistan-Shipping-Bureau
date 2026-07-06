# Secure MCQ / Proctored Assessment Update

## What was added

1. **Professional pre-test start screen**
   - Trainee/assigned user sees a secure MCQ start page before questions appear.
   - It shows duration, number of questions, passing marks, and one-attempt warning.
   - User must confirm readiness before starting.

2. **Trainer/Admin exam settings**
   - MCQ duration in minutes can be set from Training Details.
   - Passing marks are configurable.
   - Camera required, full-screen required, and one-attempt policy are configurable.
   - New courses default to one attempt only, camera required, full-screen required, and 30 minutes.

3. **Camera and full-screen proctoring panel**
   - When the exam starts, the app requests camera access.
   - A sticky secure assessment panel appears with countdown timer and camera preview.
   - The page attempts to enter full-screen mode.
   - If the user blocks camera, changes tab, exits full-screen, or window loses focus, the attempt is submitted with a proctoring flag.

4. **One-attempt locking**
   - After submission, the user sees a professional result card.
   - The same assigned user cannot retake the same MCQ assessment when one-attempt mode is enabled.
   - Results are saved to `assessment_history` and `training_records`.

5. **Auto-submit on screen violation**
   - Common violations are recorded:
     - `camera-not-allowed`
     - `tab-hidden`
     - `window-blur`
     - `fullscreen-exit`
     - `time-expired`
   - The attempt is submitted and locked with available answers saved.

6. **Management can take training**
   - Management role now has access to the Training page.
   - Admin/Trainer can include Management in assigned roles.
   - Mandatory training assignment flag added for authorization/readiness workflow.

## Important technical note

Streamlit cannot provide a true military-grade or university-grade browser lockdown because normal web browsers do not allow a website to fully prevent Alt+Tab, browser close, power off, second device use, or OS-level switching. This update provides the strongest practical Streamlit-based protection using camera access, full-screen request, tab visibility detection, focus detection, timer, one-attempt lock, and audit/proctoring flags.

For stronger production proctoring, use a dedicated React/Next.js exam frontend with a custom Streamlit component or integrate a commercial proctoring service / locked browser.

## Database columns added

### `trainings`
- `exam_duration_minutes`
- `exam_fullscreen_required`
- `exam_camera_required`
- `exam_one_attempt_only`

### `training_records`
- `mandatory_training`
- `exam_started_on`
- `exam_submitted_on`
- `exam_violation`
- `exam_answers_json`

### `assessment_history`
- `duration_minutes`
- `violation`
- `answers_json`

These columns are included in new-table creation and also attempted through lightweight schema migration for existing Supabase/PostgreSQL deployments.
