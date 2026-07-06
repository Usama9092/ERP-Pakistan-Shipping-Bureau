# Trainer/Tutor Candidate Tracking + Admin/Management Training Update

## Added

1. **My Training page for every role**
   - CEO, Management, Admin, Trainer, Tutor/Mentor and all operational users can now open their own assigned trainings.
   - This page is read-only for training material and lets the logged-in person complete assigned material, recordings, LMS and MCQs.
   - Admin/Management/CEO can take training without disturbing their operational dashboards.

2. **Assigned Candidates page**
   - Trainer can view all candidates assigned to trainings delivered by that trainer.
   - Tutor/Mentor can view all candidates assigned to trainings where they are selected as tutor/coach or where they assigned/coached the training.
   - Admin/Management can view all assigned candidates.

3. **Candidate status tracking shown to Trainer/Tutor**
   - Training title
   - Candidate name
   - Candidate role/department
   - Attendance status
   - Material access status
   - Recording access status
   - LMS status
   - MCQ result
   - Score
   - Completion status
   - Progress percentage
   - Due date
   - Certificate status
   - Trainer and Tutor names

4. **Training-wise performance summary**
   - Assigned users
   - Completed users
   - Pending users
   - Failed/flagged users
   - Average score
   - Completion percentage

5. **Passed / Completed / Pending / Overdue views**
   - Separate tabs are available for quick monitoring.

6. **Tutor assignment in training setup**
   - Training creation/editing now supports Tutor/Mentor / Technical Coach selection.
   - Tutor fields are saved in trainings and person-wise training records.

7. **Exports**
   - Assigned candidate status CSV
   - Training-wise summary CSV

## New/Updated Database Fields

The app migration now adds these fields automatically where missing:

- trainings.tutor_id
- trainings.tutor_name
- training_records.tutor_id
- training_records.tutor_name

## Workflow

Admin/Trainer/Tutor creates training -> selects Trainer and optional Tutor/Mentor -> assigns training to persons or roles -> system creates person-wise records -> Trainer/Tutor opens Assigned Candidates -> monitors attendance, completion, pass/fail, score, certificate and overdue status.

Admin/Management/CEO can open **My Training** to take assigned trainings like any other person.
