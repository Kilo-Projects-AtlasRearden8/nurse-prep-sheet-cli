"""Nurse Shift Prep Sheet CLI.

A small, local-first command-line tool for building a nurse shift prep
sheet: patient list, tasks, and priorities, saved to local JSON with a
printable text output.

Education only - never medical advice. This tool does not replace
clinical judgment, facility policy, or provider orders.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .formatter import DISCLAIMER, format_patient, format_sheet
from .models import ShiftSheet
from .prep_sheet import (
    PrepSheetError,
    add_patient,
    add_task,
    mark_task_done,
    mark_task_pending,
    remove_patient,
    sheet_summary,
)
from .storage import load_sheet, resolve_storage_path, save_sheet


def _load(path_arg: str | None) -> tuple[ShiftSheet, Path]:
    path = resolve_storage_path(path_arg)
    return load_sheet(path), path


def _save(sheet: ShiftSheet, path: Path) -> None:
    save_sheet(sheet, path)


def cmd_init(args: argparse.Namespace) -> int:
    path = resolve_storage_path(args.storage)
    sheet = ShiftSheet(
        unit=args.unit or "",
        shift=args.shift or "",
        date=args.date or "",
    )
    save_sheet(sheet, path)
    print(f"Initialized shift sheet at {path}")
    print(format_sheet(sheet))
    return 0


def cmd_add_patient(args: argparse.Namespace) -> int:
    sheet, path = _load(args.storage)
    try:
        patient = add_patient(
            sheet,
            name=args.name,
            room=args.room,
            diagnosis=args.diagnosis,
            code_status=args.code_status,
            allergies=args.allergies,
        )
    except PrepSheetError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    save_sheet(sheet, path)
    print(f"Added patient {patient.id}: {patient.name}")
    return 0


def cmd_add_task(args: argparse.Namespace) -> int:
    sheet, path = _load(args.storage)
    try:
        task = add_task(
            sheet,
            patient_id=args.patient,
            description=args.description,
            priority=args.priority,
            due=args.due,
        )
    except PrepSheetError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    save_sheet(sheet, path)
    print(f"Added task {task.id} for patient {args.patient}: {task.description}")
    return 0


def cmd_list_patients(args: argparse.Namespace) -> int:
    sheet, _ = _load(args.storage)
    if not sheet.patients:
        print("No patients on this sheet.")
        return 0
    print(f"Unit: {sheet.unit or '(not set)'}  Shift: {sheet.shift or '(not set)'}  Date: {sheet.date or '(not set)'}")
    print("-" * 40)
    for patient in sheet.patients:
        print(
            f"{patient.id} | {patient.name} | Room {patient.room or '-'} | "
            f"{patient.pending_task_count()} pending task(s)"
        )
    return 0


def cmd_list_tasks(args: argparse.Namespace) -> int:
    sheet, _ = _load(args.storage)
    patient = sheet.patient_by_id(args.patient)
    if patient is None:
        print(f"error: patient '{args.patient}' not found", file=sys.stderr)
        return 1
    print(f"Tasks for {patient.name} (Room {patient.room or '-'})")
    print("-" * 40)
    if not patient.tasks:
        print("(none)")
        return 0
    for task in patient.tasks:
        box = "[X]" if task.done else "[ ]"
        due = f" due {task.due}" if task.due else ""
        print(f"{task.id} | {box} {task.priority.upper():6} {task.description}{due}")
    return 0


def cmd_done(args: argparse.Namespace) -> int:
    sheet, path = _load(args.storage)
    try:
        task = mark_task_done(sheet, args.patient, args.task)
    except PrepSheetError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    save_sheet(sheet, path)
    print(f"Marked task {task.id} done: {task.description}")
    return 0


def cmd_pending(args: argparse.Namespace) -> int:
    sheet, path = _load(args.storage)
    try:
        task = mark_task_pending(sheet, args.patient, args.task)
    except PrepSheetError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    save_sheet(sheet, path)
    print(f"Marked task {task.id} pending: {task.description}")
    return 0


def cmd_remove_patient(args: argparse.Namespace) -> int:
    sheet, path = _load(args.storage)
    try:
        patient = remove_patient(sheet, args.patient)
    except PrepSheetError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    save_sheet(sheet, path)
    print(f"Removed patient {patient.id}: {patient.name}")
    return 0


def cmd_sheet(args: argparse.Namespace) -> int:
    sheet, _ = _load(args.storage)
    if args.patient:
        patient = sheet.patient_by_id(args.patient)
        if patient is None:
            print(f"error: patient '{args.patient}' not found", file=sys.stderr)
            return 1
        print(format_patient(patient))
    else:
        print(format_sheet(sheet))
    return 0


def cmd_summary(args: argparse.Namespace) -> int:
    sheet, _ = _load(args.storage)
    print(sheet_summary(sheet))
    print(DISCLAIMER)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nurse-prep",
        description="Nurse Shift Prep Sheet - education only, never medical advice.",
    )
    parser.add_argument(
        "--storage",
        default=None,
        help="Path to the local JSON storage file (default: ~/.nurse-prep-sheet/shift.json)",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Initialize a new shift sheet file")
    p_init.add_argument("--unit", default="", help="Unit name")
    p_init.add_argument("--shift", default="", help="Shift label (e.g. 7a-7p)")
    p_init.add_argument("--date", default="", help="Shift date")
    p_init.set_defaults(func=cmd_init)

    p_add_patient = sub.add_parser("add-patient", help="Add a patient to the sheet")
    p_add_patient.add_argument("name", help="Patient name")
    p_add_patient.add_argument("--room", default="", help="Room number")
    p_add_patient.add_argument("--diagnosis", default="", help="Diagnosis")
    p_add_patient.add_argument("--code-status", default="", dest="code_status", help="Code status")
    p_add_patient.add_argument("--allergies", default="", help="Allergies")
    p_add_patient.set_defaults(func=cmd_add_patient)

    p_add_task = sub.add_parser("add-task", help="Add a task for a patient")
    p_add_task.add_argument("patient", help="Patient id")
    p_add_task.add_argument("description", help="Task description")
    p_add_task.add_argument("--priority", default="medium", choices=["high", "medium", "low"], help="Priority level")
    p_add_task.add_argument("--due", default="", help="Due time")
    p_add_task.set_defaults(func=cmd_add_task)

    p_list_patients = sub.add_parser("list-patients", help="List patients on the sheet")
    p_list_patients.set_defaults(func=cmd_list_patients)

    p_list_tasks = sub.add_parser("list-tasks", help="List tasks for a patient")
    p_list_tasks.add_argument("patient", help="Patient id")
    p_list_tasks.set_defaults(func=cmd_list_tasks)

    p_done = sub.add_parser("done", help="Mark a task done")
    p_done.add_argument("patient", help="Patient id")
    p_done.add_argument("task", help="Task id")
    p_done.set_defaults(func=cmd_done)

    p_pending = sub.add_parser("pending", help="Mark a task pending (not done)")
    p_pending.add_argument("patient", help="Patient id")
    p_pending.add_argument("task", help="Task id")
    p_pending.set_defaults(func=cmd_pending)

    p_remove = sub.add_parser("remove-patient", help="Remove a patient from the sheet")
    p_remove.add_argument("patient", help="Patient id")
    p_remove.set_defaults(func=cmd_remove_patient)

    p_sheet = sub.add_parser("sheet", help="Print the full shift sheet (printable)")
    p_sheet.add_argument("--patient", default=None, help="Print only one patient by id")
    p_sheet.set_defaults(func=cmd_sheet)

    p_summary = sub.add_parser("summary", help="Print a short sheet summary")
    p_summary.set_defaults(func=cmd_summary)

    return parser


def main(argv: list[str] | None = None) -> int:
    print(DISCLAIMER, file=sys.stderr)
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
