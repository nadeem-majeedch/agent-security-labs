# Getting Started

AgentSec Labs is a set of **eight small, offline, deterministic labs** for
learning AI-agent security by reading the traces the labs produce. You do not
need an API key, a network connection or any security background to begin.

> These labs are educational infrastructure. The model is a deterministic
> **fixture**, so what you observe is the **mechanics** of a security boundary —
> not the behaviour of a real model. They are **not a benchmark** and make **no
> research claim**. There is deliberately **no LAB-08**.

## What you need

- Python 3.11 or newer (`py` on Windows, `python` elsewhere).
- A terminal in the repository root.
- Basic familiarity with the command line and with JSON/JSONL.

## 1. Install

```bash
py -m pip install -e ".[dev]"
```

Nothing else is required: the labs run offline with the in-memory sandbox tools.

## 2. Run your first lab

```bash
PYTHONPATH=src py -m agentsec run labs/LAB-00-setup/config.yaml
PYTHONPATH=src py -m agentsec inspect runs/lab00_setup/trace.jsonl
PYTHONPATH=src py -m agentsec evaluate runs/lab00_setup/trace.jsonl
```

The first command runs the experiment and writes a **trace**; the second lists
its events in order; the third evaluates the trace on its own — it does **not**
re-run the experiment.

## 3. Work through the labs in order

Begin with **LAB-00** and continue through **LAB-07**. The **Lab Map** describes
what each lab teaches; every lab's own page has the commands to run, the
questions to answer and a completion checklist.

## 4. Learn to read a trace

- **Understanding Traces** — an event-by-event walkthrough of the trace each lab
  actually produces, with what to look for and what the events do **not** prove.
- **Practice** — exercises where you decide, from the trace alone, whether a tool
  was requested, denied, held for approval, or actually executed.

## 5. Check your setup stays healthy

```bash
PYTHONPATH=src py -m agentsec labs check
```

This re-runs every lab and confirms each still produces its declared result. See
**Local Verification** for what it checks and what it deliberately does not.

## The one habit to build

The goal of the whole sequence is to answer a single question **with evidence**:

> **"What can I actually observe in the trace?"**

Keep four things separate as you read — **what was requested**, **what was
decided**, **what executed**, and **what changed** — and name the event that
supports each claim.
