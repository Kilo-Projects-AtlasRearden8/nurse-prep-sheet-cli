"""Tests for the Nurse Shift Prep Sheet entry logic."""

from __future__ import annotations

import os
import tempfile
import unittest

from nurse_prep_sheet.models import Patient, PRIORITY_LEVELS, ShiftSheet, Task
from nurse_prep_sheet.prep_sheet import (
    PrepSheetError,
    add_patient,
    add_task,
    mark_task_done,
    mark_task_pending,
    remove_patient,
    sheet_summary,
)
from nurse_prep_sheet.storage import load_sheet, save_sheet


class TaskTests(unittest.TestCase):
    def test_valid_priorities(self):
        for priority in PRIORITY_LEVELS:
            task = Task(description="check vitals", priority=priority)
            self.assertEqual(task.priority, priority)

    def test_invalid_priority_raises(self):
        with self.assertRaises(ValueError):
            Task(description="x", priority="urgent")

    def test_done_defaults_false(self):
        task = Task(description="x")
        self.assertFalse(task.done)


class PatientTests(unittest.TestCase):
    def test_add_task_and_pending_count(self):
        patient = Patient(name="Dylan Asdale", room="312")
        patient.add_task(Task(description="med pass", priority="high"))
        patient.add_task(Task(description="charting", priority="low"))
        self.assertEqual(patient.pending_task_count(), 2)
        self.assertEqual(len(patient.high_priority_pending()), 1)

    def test_task_by_id(self):
        patient = Patient(name="Test")
        patient.add_task(Task(description="first"))
        patient.add_task(Task(description="second"))
        self.assertIsNotNone(patient.task_by_id("t1"))
        self.assertIsNone(patient.task_by_id("nope"))

    def test_high_priority_pending_excludes_done(self):
        patient = Patient(name="Test")
        t1 = Task(description="done high", priority="high")
        t1.done = True
        patient.add_task(t1)
        patient.add_task(Task(description="pending low", priority="low"))
        self.assertEqual(len(patient.high_priority_pending()), 0)
        self.assertEqual(patient.pending_task_count(), 1)

    def test_round_trip_dict(self):
        patient = Patient(name="R.T.", room="4", allergies="NKDA")
        patient.add_task(Task(description="ambulate", priority="medium", due="10:00"))
        restored = Patient.from_dict(patient.to_dict())
        self.assertEqual(restored.name, patient.name)
        self.assertEqual(len(restored.tasks), 1)
        self.assertEqual(restored.tasks[0].priority, "medium")
        self.assertEqual(restored.tasks[0].due, "10:00")


class ShiftSheetTests(unittest.TestCase):
    def test_add_and_find_patient(self):
        sheet = ShiftSheet()
        sheet.add_patient(Patient(name="One"))
        sheet.add_patient(Patient(name="Two"))
        self.assertIsNotNone(sheet.patient_by_name("one"))
        self.assertIsNone(sheet.patient_by_name("ghost"))

    def test_round_trip_dict(self):
        sheet = ShiftSheet(unit="ICU", shift="7p-7a", date="2026-10-29")
        sheet.add_patient(Patient(name="One", room="1"))
        restored = ShiftSheet.from_dict(sheet.to_dict())
        self.assertEqual(restored.unit, "ICU")
        self.assertEqual(len(restored.patients), 1)
        self.assertEqual(restored.patients[0].name, "One")


class PrepSheetLogicTests(unittest.TestCase):
    def setUp(self):
        self.sheet = ShiftSheet(unit="Floor", shift="days", date="2026-10-29")
        self.patient = add_patient(self.sheet, "Jane Doe", room="210", allergies="PCN")

    def test_add_patient_validates_name(self):
        with self.assertRaises(PrepSheetError):
            add_patient(self.sheet, "   ")
        with self.assertRaises(PrepSheetError):
            add_patient(self.sheet, "Jane Doe")

    def test_add_task_validates(self):
        task = add_task(self.sheet, self.patient.id, "give meds", priority="high", due="09:00")
        self.assertEqual(task.priority, "high")
        self.assertEqual(task.due, "09:00")
        with self.assertRaises(PrepSheetError):
            add_task(self.sheet, self.patient.id, "   ")
        with self.assertRaises(PrepSheetError):
            add_task(self.sheet, self.patient.id, "x", priority="critical")
        with self.assertRaises(PrepSheetError):
            add_task(self.sheet, "nope", "x")

    def test_mark_done_and_pending(self):
        task = add_task(self.sheet, self.patient.id, "check vitals")
        mark_task_done(self.sheet, self.patient.id, task.id)
        self.assertTrue(task.done)
        mark_task_pending(self.sheet, self.patient.id, task.id)
        self.assertFalse(task.done)

    def test_remove_patient(self):
        removed = remove_patient(self.sheet, self.patient.id)
        self.assertEqual(removed.name, "Jane Doe")
        self.assertEqual(len(self.sheet.patients), 0)
        with self.assertRaises(PrepSheetError):
            remove_patient(self.sheet, self.patient.id)

    def test_summary(self):
        add_task(self.sheet, self.patient.id, "med pass", priority="high")
        summary = sheet_summary(self.sheet)
        self.assertIn("patients: 1", summary)
        self.assertIn("pending: 1", summary)


class StorageTests(unittest.TestCase):
    def test_save_and_load_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "shift.json")
            sheet = ShiftSheet(unit="ED", shift="nights", date="2026-10-29")
            patient = add_patient(sheet, "A. Patient", room="7")
            add_task(sheet, patient.id, "admit", priority="high")
            save_sheet(sheet, path)
            loaded = load_sheet(path)
            self.assertEqual(loaded.unit, "ED")
            self.assertEqual(len(loaded.patients), 1)
            self.assertEqual(loaded.patients[0].name, "A. Patient")
            self.assertEqual(len(loaded.patients[0].tasks), 1)
            self.assertEqual(loaded.patients[0].tasks[0].priority, "high")

    def test_load_missing_file_returns_empty_sheet(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "missing.json")
            sheet = load_sheet(path)
            self.assertEqual(len(sheet.patients), 0)


if __name__ == "__main__":
    unittest.main()
