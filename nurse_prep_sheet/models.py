"""Data models for the Nurse Shift Prep Sheet CLI.

Education-only tool. This is not medical advice and does not replace
clinical judgment, facility policy, or provider orders.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


PRIORITY_LEVELS = ("high", "medium", "low")


def now_iso() -> str:
    """Return the current UTC time as an ISO-8601 string."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass
class Task:
    """A single task for a patient on a shift."""

    description: str
    priority: str = "medium"
    due: Optional[str] = None
    done: bool = False
    created_at: str = field(default_factory=now_iso)
    id: Optional[str] = None

    def __post_init__(self) -> None:
        if self.priority not in PRIORITY_LEVELS:
            raise ValueError(f"priority must be one of {PRIORITY_LEVELS}")


@dataclass
class Patient:
    """A patient on the current shift."""

    name: str
    room: str = ""
    diagnosis: str = ""
    code_status: str = ""
    allergies: str = ""
    tasks: list[Task] = field(default_factory=list)
    created_at: str = field(default_factory=now_iso)
    id: Optional[str] = None

    def task_by_id(self, task_id: str) -> Optional[Task]:
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def add_task(self, task: Task) -> None:
        if task.id is None:
            task.id = f"t{len(self.tasks) + 1}"
        self.tasks.append(task)

    def pending_task_count(self) -> int:
        return sum(1 for task in self.tasks if not task.done)

    def high_priority_pending(self) -> list[Task]:
        return [
            task
            for task in self.tasks
            if not task.done and task.priority == "high"
        ]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "room": self.room,
            "diagnosis": self.diagnosis,
            "code_status": self.code_status,
            "allergies": self.allergies,
            "created_at": self.created_at,
            "tasks": [
                {
                    "id": task.id,
                    "description": task.description,
                    "priority": task.priority,
                    "due": task.due,
                    "done": task.done,
                    "created_at": task.created_at,
                }
                for task in self.tasks
            ],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Patient":
        patient = cls(
            name=data["name"],
            room=data.get("room", ""),
            diagnosis=data.get("diagnosis", ""),
            code_status=data.get("code_status", ""),
            allergies=data.get("allergies", ""),
            created_at=data.get("created_at", now_iso()),
        )
        patient.id = data.get("id")
        for task_data in data.get("tasks", []):
            task = Task(
                description=task_data["description"],
                priority=task_data.get("priority", "medium"),
                due=task_data.get("due"),
                done=task_data.get("done", False),
                created_at=task_data.get("created_at", now_iso()),
            )
            task.id = task_data.get("id")
            patient.tasks.append(task)
        return patient


@dataclass
class ShiftSheet:
    """A collection of patients for one shift."""

    shift: str = ""
    date: str = ""
    unit: str = ""
    patients: list[Patient] = field(default_factory=list)

    def patient_by_id(self, patient_id: str) -> Optional[Patient]:
        for patient in self.patients:
            if patient.id == patient_id:
                return patient
        return None

    def patient_by_name(self, name: str) -> Optional[Patient]:
        for patient in self.patients:
            if patient.name.lower() == name.lower():
                return patient
        return None

    def add_patient(self, patient: Patient) -> None:
        if patient.id is None:
            patient.id = f"p{len(self.patients) + 1}"
        self.patients.append(patient)

    def to_dict(self) -> dict:
        return {
            "shift": self.shift,
            "date": self.date,
            "unit": self.unit,
            "patients": [patient.to_dict() for patient in self.patients],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ShiftSheet":
        sheet = cls(
            shift=data.get("shift", ""),
            date=data.get("date", ""),
            unit=data.get("unit", ""),
        )
        for patient_data in data.get("patients", []):
            sheet.patients.append(Patient.from_dict(patient_data))
        return sheet
