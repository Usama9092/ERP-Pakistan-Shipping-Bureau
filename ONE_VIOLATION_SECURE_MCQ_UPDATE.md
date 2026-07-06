# One-Violation Secure MCQ Update

This build updates the trainee MCQ exam flow with the requested PSB policy.

## Exam flow

Start Test → Full Screen Mandatory → Camera ON → Timer Starts → Questions Randomized → Answer Options Randomized → Auto Save Every 10 Seconds → One Screen/Camera/Fullscreen Violation → Auto Submit → Score Generated → Result Stored.

## Implemented behavior

- MCQs appear only after the trainee confirms readiness and clicks **Start Secure MCQ Assessment**.
- Exam start time is saved in `training_records.exam_started_on`.
- Full-screen is requested automatically and a manual **Enter Full Screen** button remains visible.
- Camera permission is requested. If camera is denied, the attempt is auto-submitted.
- Timer starts immediately after the exam begins.
- Questions are randomized per assessment record.
- Answer options are randomized per question.
- Answers are auto-saved every 10 seconds into `training_records.exam_answers_json`.
- Auto-save timestamp is stored in `training_records.exam_autosaved_on`.
- If the user changes tab, leaves the window, exits full-screen, blocks camera, or the timer expires, the system records the violation and submits the test.
- Policy is now **1 violation only**. Any single violation locks and submits the attempt.
- Manual submit still works when the trainee completes the test within time.
- Result, score, answers, violation flag, and remarks are stored in `assessment_history` and `training_records`.

## Violation events

- `camera-not-allowed`
- `tab-hidden`
- `window-blur`
- `fullscreen-exit`
- `time-expired`

## Database columns added

- `training_records.exam_autosaved_on`
- `training_records.exam_question_order_json`
- Existing secure exam fields are also retained: `exam_started_on`, `exam_submitted_on`, `exam_violation`, `exam_answers_json`.

## Streamlit limitation

This is the strongest practical lockdown available inside Streamlit/browser execution. A browser cannot fully prevent OS-level Alt+Tab, shutdown, second-device cheating, or network disconnects. Those cases are handled by audit flags and one-attempt locking where detectable.
