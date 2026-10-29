"""Printable text output for nurse shift prep sheets.

Produces plain-text sheets suitable for printing or copying into a
handoff note. Education-only tool - not medical advice.
"""

from __future__ import annotations

from .models import Patient, ShiftSheet

DISCLAIMER = (
    "EDUCATION ONLY - NOT MEDICAL ADVICE. "
    "This sheet does not replace clinical judgment, facility policy, "
    "provider orders, or provider direction. Always verify with the "
    "care team before acting."
)

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def _sort_tasks(tasks):
    return sorted(tasks, key=lambda t: (PRIORITY_ORDER.get(t.priority, 1), t.description.lower()))


def format_sheet(sheet: ShiftSheet) -> str:
    """Return a full printable text representation of the shift sheet."""
    lines: list[str] = []
    lines.append("NURSE SHIFT PREP SHEET")
    lines.append("=" * 32)
    lines.append("")
    lines.append(f"Unit:     {sheet.unit or '(not set)'}")
    lines.append(f"Shift:    {sheet.shift or '(not set)'}")
    lines.append(f"Date:     {sheet.date or '(not set)'}")
    lines.append("")
    lines.append(DISCLAIMER)
    lines.append("")
    lines.append(f"Patients: {len(sheet.patients)}")
    lines.append("-" * 32)
    lines.append("")

    if not sheet.patients:
        lines.append("No patients on this sheet yet.")
        lines.append("")
        lines.append("Add patients with: nurse-prep add-patient ...")
        lines.append("")
        lines.append("End of sheet")
        return "\n".join(lines)

    for index, patient in enumerate(sheet.patients, start=1):
        if index > 1:
            lines.append("")
            lines.append("=" * 32)
            lines.append("")
        lines.append(f"{index}. {patient.name}")
        lines.append(f"   Room:        {patient.room or '(not set)'}")
        lines.append(f"   Diagnosis:   {patient.diagnosis or '(not set)'}")
        lines.append(f"   Code status: {patient.code_status or '(not set)'}")
        lines.append(f"   Allergies:   {patient.allergies or '(none recorded)'}")
        if patient.tasks:
            lines.append("   Tasks:")
            for task in _sort_tasks(patient.tasks):
                box = "[X]" if task.done else "[ ]"
                due = f" due {task.due}" if task.due else ""
                lines.append(
                    f"     {box} {task.priority.upper():6} {task.description}{due}"
                )
        else:
            lines.append("   Tasks: (none)")
        lines.append(f"   Pending: {patient.pending_task_count()}")

    lines.append("")
    lines.append("-" * 32)
    lines.append("End of sheet")
    lines.append(DISCLAIMER)
    return "\n".join(lines)


def format_patient(patient: Patient) -> str:
    """Return a printable text representation of a single patient."""
    lines: list[str] = []
    lines.append(f"PATIENT: {patient.name}")
    lines.append("-" * 32)
    lines.append(f"Room:        {patient.room or '(not set)'}")
    lines.append(f"Diagnosis:   {patient.diagnosis or '(not set)'}")
    lines.append(f"Code status: {patient.code_status or '(not set)'}")
    lines.append(f"Allergies:   {patient.allergies or '(none recorded)'}")
    lines.append("")
    if patient.tasks:
        lines.append("TASKS:")
        for task in _sort_tasks(patient.tasks):
            box = "[X]" if task.done else "[ ]"
            due = f" due {task.due}" if task.due else ""
            lines.append(
                f"  {box} {task.priority.upper():6} {task.description}{due}"
            )
        lines.append("")
        lines.append(f"Pending: {patient.pending_task_count()}")
    else:
        lines.append("TASKS: (none)")
    lines.append("")
    lines.append(DISCLAIMER)
    return "\n".join(lines)
