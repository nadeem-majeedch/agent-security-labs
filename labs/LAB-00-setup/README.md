# LAB-00 — Setup & Environment Verification

This is the **warm-up lab**. It contains no attack and no defence. You run one
tiny experiment and confirm that your machine can:

- import the `agentsec` package,
- use the command-line interface,
- run the deterministic **mock model** and the **sandbox tools**,
- load an example **policy** and **configuration**,
- produce a **trace** and **evaluate** it — all **offline**.

If this lab works, every later lab will work too.

> This is educational infrastructure. It makes no research claim and is not a
> benchmark.

## Learning objectives

By the end of this lab you should be able to:

1. Run the lab CLI from a checkout.
2. Explain why the lab needs no API keys and no network.
3. Find where a run's trace file is written.
4. Read the descriptive evaluation of a finished run.

## Prerequisites

- Python 3.11 or newer (`py` on Windows, `python` elsewhere).
- A terminal in the repository root.
- Basic command-line and JSON/JSONL familiarity.

No security knowledge, API keys or internet connection are required.

## Safety

Everything in this lab is local, offline and synthetic:

- **Tools are sandboxed.** The calculator only does arithmetic; the virtual
  filesystem is in-memory; the mock database is in-memory with synthetic rows.
- **No real credentials** are requested or read.
- **No external services** are contacted.
- The model is a **deterministic fixture**, not a real LLM.

## Procedure

### 1. Check the package imports

```bash
PYTHONPATH=src py -c "import agentsec; print(agentsec.__version__)"
```

### 2. Check the CLI is available

```bash
PYTHONPATH=src py -m agentsec --help
```

### 3. Run the setup experiment

```bash
PYTHONPATH=src py -m agentsec run labs/LAB-00-setup/config.yaml
```

### 4. Look at the trace it produced

```bash
PYTHONPATH=src py -m agentsec inspect runs/lab00_setup/trace.jsonl
```

### 5. Evaluate the trace on its own

```bash
PYTHONPATH=src py -m agentsec evaluate runs/lab00_setup/trace.jsonl
```

> If the package is installed (`py -m pip install -e ".[dev]"`) you may drop the
> `PYTHONPATH=src` prefix and use the `agentsec` command directly.

## What to look for

- Step 2 prints a help screen listing the `run`, `evaluate` and `inspect`
  commands.
- Step 3 prints a completed run, a trace path and a short evaluation summary.
- Step 4 prints the run id and the ordered list of trace events.
- Step 5 prints the same descriptive evaluation that you saw in step 3, but it
  reads only the trace file — it does **not** run the experiment again.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `ModuleNotFoundError: agentsec` | `PYTHONPATH=src` missing | Prefix the command, or install with `py -m pip install -e ".[dev]"`. |
| `command not found: py` | `py` is Windows-only | Use `python` instead of `py`. |
| `could not read ... config` | Wrong working directory | Run from the repository root. |
| `unknown mock script` | Typo in `mock_script` | Use one of the names in `agentsec.models.mock.SCRIPT_FACTORIES`. |

## Completion checklist

- [ ] The import check printed a version number.
- [ ] `--help` listed the `run`, `evaluate` and `inspect` commands.
- [ ] The experiment completed and printed a trace path.
- [ ] `inspect` showed the trace events in order.
- [ ] `evaluate` printed a descriptive evaluation.
- [ ] `runs/lab00_setup/trace.jsonl` exists and is valid JSON on every line.

When all six are checked, this lab is complete. Continue to
`labs/LAB-01-benign-agent`.
