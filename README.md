# Nurse Shift Prep Sheet CLI

A small, local-first command-line tool for building a nurse shift prep
sheet: patient list, tasks, and priorities, saved to a local JSON file
with printable text output.

Built and published by **Asdale Dynamics, LLC** (Indiana, formed October
2026) — beginner-friendly AI education, books and guides, and practical
tools you can actually use. Learn more at dylanasdale.github.io.

## Education only — not medical advice

This tool is for education and personal organization only. It is **not**
medical advice, and it does not replace clinical judgment, facility
policy, provider orders, or direction from the care team. Always verify
with the care team before acting on anything in a prep sheet.

Every time you run the CLI, and on every printed sheet, you'll see this
reminder:

> EDUCATION ONLY — NOT MEDICAL ADVICE. This sheet does not replace
> clinical judgment, facility policy, provider orders, or provider
> direction. Always verify with the care team before acting.

No patient data is stored by Asdale Dynamics, LLC. Everything stays on
your machine in a local JSON file. No network access, no accounts, no
API keys, no tracking.

## What it does

- Add patients with room, diagnosis, code status, and allergies
- Add tasks per patient with a priority (high / medium / low) and due time
- Mark tasks as done or back to pending
- List all patients on a shift, or list one patient's tasks
- Print a full shift sheet (plain text, printer-friendly) or a single
  patient summary
- Print a short summary with pending and high-priority task counts
- Save everything locally as JSON so your data never leaves your computer

## Install

You can run the tool without installing anything:

```bash
python3 -m nurse_prep_sheet --help
```

Or install it so you get the `nurse-prep` command:

```bash
cd nurse-prep-sheet-cli
python3 -m pip install -e .
```

If your system blocks pip installs (PEP 668 "externally managed"),
create a virtual environment first:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e .
```

## Usage, step by step

### 1. Start a new shift sheet

```bash
nurse-prep init --unit MedSurg --shift "7a-7p" --date 2026-10-29
```

This creates a local JSON file (by default at
`~/.nurse-prep-sheet/shift.json`) and prints a blank sheet.

### 2. Add a patient

```bash
nurse-prep add-patient "Jane Doe" --room 210 --diagnosis pneumonia --allergies "PCN"
```

You can also add code status:

```bash
nurse-prep add-patient "John Smith" --room 302 --code-status "DNR"
```

### 3. Add tasks for a patient

Use the patient id (shown when you add the patient, e.g. `p1`):

```bash
nurse-prep add-task p1 "morning med pass" --priority high --due 09:00
nurse-prep add-task p1 "ambulate in hall" --priority medium --due 10:30
nurse-prep add-task p1 "charting" --priority low
```

### 4. Mark tasks done (or back to pending)

```bash
nurse-prep done p1 t1
nurse-prep pending p1 t1
```

### 5. See your patients

```bash
nurse-prep list-patients
```

### 6. See one patient's tasks

```bash
nurse-prep list-tasks p1
```

### 7. Print the full sheet

```bash
nurse-prep sheet
```

Print one patient only:

```bash
nurse-prep sheet --patient p1
```

### 8. Quick summary

```bash
nurse-prep summary
```

### Use a different storage file

```bash
nurse-prep --storage /tmp/my-shift.json init
```

## Example printed sheet

```
NURSE SHIFT PREP SHEET
================================

Unit:     MedSurg
Shift:    7a-7p
Date:     2026-10-29

EDUCATION ONLY — NOT MEDICAL ADVICE. ...

Patients: 1
--------------------------------

1. Jane Doe
   Room:        210
   Diagnosis:   pneumonia
   Code status: (not set)
   Allergies:   PCN
   Tasks:
     [X] HIGH   morning med pass due 09:00
     [ ] MEDIUM ambulate in hall due 10:30
   Pending: 1

--------------------------------
End of sheet
EDUCATION ONLY — NOT MEDICAL ADVICE. ...
```

## Tests

```bash
python3 -m unittest discover -s tests
```

16 tests, Python standard library only. They cover patient and task
entry logic, priority validation, done/pending transitions, and JSON
save/load round trips.

## About Asdale Dynamics, LLC

Asdale Dynamics, LLC (Indiana, formed October 2026) is founded by Dylan
Asdale, a registered nurse turned AI author. The LLC publishes
beginner-friendly AI education — books and guides like *The Massive AI
Manual* — plus open-source tools and templates: prompt tools, local-LLM
utilities, MCP servers, agent skills, small-business and author tools,
and accessible life-admin helpers including healthcare-worker AI aids
(education only, never medical advice).

Hub site: dylanasdale.github.io

## License

MIT License. Copyright (c) 2026 Asdale Dynamics, LLC. See LICENSE.
