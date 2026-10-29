"""Business logic for assembling and editing nurse shift prep sheets.

Education-only tool. Nothing here is medical advice.
"""

from __future__ import annotations

from .models import Patient, PRIORITY_LEVELS, ShiftSheet, Task


class PrepSheetError(Exception):
    """Raised when a prep sheet operation is invalid."""


def ensure_priority(priority: str) -> str:
    """Normalize and validate a priority level."""
    normalized = priority.strip().lower()
    if normalized not in PRIORITY_LEVELS:
        raise PrepSheetError(
            f"invalid priority '{priority}'; must be one of {PRIORITY_LEVELS}"
        )
    return normalized


def add_patient(
    sheet: ShiftSheet,
    name: str,
    room: str = "",
    diagnosis: str = "",
    code_status: str = "",
    allergies: str = "",
) -> Patient:
    """Add a patient to the sheet and return it."""
    if not name or not name.strip():
        raise PrepSheetError("patient name is required")
    if sheet.patient_by_name(name.strip()) is not None:
        raise PrepSheetError(f"patient '{name}' already exists on this sheet")
    patient = Patient(
        name=name.strip(),
        room=room.strip(),
        diagnosis=diagnosis.strip(),
        code_status=code_status.strip(),
        allergies=allergies.strip(),
    )
    sheet.add_patient(patient)
    return patient


def add_task(
    sheet: ShiftSheet,
    patient_id: str,
    description: str,
    priority: str = "medium",
    due: str = "",
) -> Task:
    """Add a task to a patient and return it."""
    patient = sheet.patient_by_id(patient_id)
    if patient is None:
        raise PrepSheetError(f"patient '{patient_id}' not found")
    if not description or not description.strip():
        raise PrepSheetError("task description is required")
    task = Task(
        description=description.strip(),
        priority=ensure_priority(priority),
        due=due.strip() or None,
    )
    patient.add_task(task)
    return task


def mark_task_done(sheet: ShiftSheet, patient_id: str, task_id: str) -> Task:
    """Mark a task as done and return it."""
    patient = sheet.patient_by_id(patient_id)
    if patient is None:
        raise PrepSheetError(f"patient '{patient_id}' not found")
    task = patient.task_by_id(task_id)
    if task is None:
        raise PrepSheetError(f"task '{task_id}' not found for patient '{patient_id}'")
    task.done = True
    return task


def mark_task_pending(sheet: ShiftSheet, patient_id: str, task_id: str) -> Task:
    """Mark a task as pending (not done) and return it."""
    patient = sheet.patient_by_id(patient_id)
    if patient is None:
        raise PrepSheetError(f"patient '{patient_id}' not found")
    task = patient.task_by_id(task_id)
    if task is None:
        raise PrepSheetError(f"task '{task_id}' not found for patient '{patient_id}'")
    task.done = False
    return task


def remove_patient(sheet: ShiftSheet, patient_id: str) -> Patient:
    """Remove a patient from the sheet and return it."""
    for index, patient in enumerate(sheet.patients):
        if patient.id == patient_id:
            return sheet.patients.pop(index)
    raise PrepSheetError(f"patient '{patient_id}' not found")


def sheet_summary(sheet: ShiftSheet) -> str:
    """Return a short text summary of the sheet."""
    patient_count = len(sheet.patients)
    task_count = sum(len(p.tasks) for p in sheet.patients)
    pending = sum(p.pending_task_count() for p in sheet.patients)
    high = sum(len(p.high_priority_pending()) for p in sheet.patients)
    return (
        f"{sheet.unit or 'unit'} | {sheet.shift or 'shift'} | {sheet.date or 'date'}\n"
        f"patients: {patient_count} | tasks: {task_count} | "
        f"pending: {pending} | high-priority pending: {high}"
    )
