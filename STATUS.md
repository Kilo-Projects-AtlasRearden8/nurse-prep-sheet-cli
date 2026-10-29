# STATUS — Nurse Shift Prep Sheet CLI

## What was built

A local-first Python CLI for building a nurse shift prep sheet, created
in `/workspace/kilo-lab/nurse-prep-sheet-cli`.

Package `nurse_prep_sheet/`:
- `models.py` — Patient, Task, ShiftSheet dataclasses with validation
  (priority must be high/medium/low), JSON serialization, ID assignment.
- `storage.py` — Local JSON save/load; missing file yields an empty
  sheet; default path `~/.nurse-prep-sheet/shift.json`, overridable with
  `--storage`.
- `prep_sheet.py` — Entry logic: add patient/task, mark done/pending,
  remove patient, sheet summary (counts of patients, tasks, pending,
  high-priority pending).
- `formatter.py` — Printable plain-text sheet output with per-patient
  rooms, diagnosis, code status, allergies, checkboxed tasks sorted by
  priority, and the education-only disclaimer on every sheet.
- `cli.py` — argparse CLI: init, add-patient, add-task, list-patients,
  list-tasks, done, pending, remove-patient, sheet, summary. Console
  script entry point `nurse-prep`.
- `__main__.py` — supports `python3 -m nurse_prep_sheet`.

Tests `tests/test_prep_sheet.py`: 16 unittest tests using only the
Python standard library, covering model validation, entry logic, and
JSON round trips.

Other files: `README.md`, `LICENSE` (MIT),
`pyproject.toml` (with `nurse-prep` console script), `STATUS.md`.

## How to run

```bash
cd /workspace/kilo-lab/nurse-prep-sheet-cli
python3 -m pip install -e .        # optional, provides the nurse-prep command
python3 -m nurse_prep_sheet init --unit MedSurg --shift "7a-7p" --date 2026-10-29
python3 -m nurse_prep_sheet add-patient "Jane Doe" --room 210 --diagnosis pneumonia --allergies "PCN"
python3 -m nurse_prep_sheet add-task p1 "morning med pass" --priority high --due 09:00
python3 -m nurse_prep_sheet sheet
python3 -m nurse_prep_sheet summary
```

Or with the installed entry point:

```bash
nurse-prep <command>
```

Tests:

```bash
python3 -m unittest discover -s tests
```

## Verification results

- `python3 -m unittest discover -s tests` — **OK, 16 tests, 0 failures,
  0 errors** (Python 3.13.5).
- CLI smoke test — **OK**: init, add-patient, add-task, mark done,
  print full sheet, print summary all ran successfully and produced
  correct printable output with checkboxes, priority sorting, pending
  counts, and disclaimers.

## Known gaps

- No web/GUI interface; CLI and printable text only.
- Storage is a single JSON file per path; no concurrent-write locking or
  sync/backup features.
- Task due times are free-form strings, not parsed/scheduled.
- No patient edit command (use remove + re-add to change details).
- The default storage location is `~/.nurse-prep-sheet/shift.json`;
  there is no auto-detected per-shift rotation — each run appends to
  the same sheet file unless `--storage` points elsewhere.

## Credits

Built by Asdale Dynamics, LLC (Indiana, formed October 2026), founded by
Dylan Asdale, registered nurse turned AI author. Hub site:
dylanasdale.github.io. Education only — never medical advice.

License: MIT, Copyright (c) 2026 Asdale Dynamics, LLC.
