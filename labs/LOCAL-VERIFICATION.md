# Local verification — `agentsec labs check`

One offline command verifies that the labs still behave as documented. It
re-runs **LAB-00 … LAB-07** through the existing deterministic machinery and
checks each result against the lab's own declared expectations
(`scenario.yaml` → `expected`). LAB-00 is a setup smoke test and ships no
`scenario.yaml`, so it is checked only for a run that completes and produces a
final answer.

```bash
agentsec labs check
```

```
LAB SELF-CHECK
==============

LAB-00  PASS
LAB-01  PASS
LAB-02  PASS
LAB-03  PASS
LAB-04  PASS
LAB-05  PASS
LAB-06  PASS
LAB-07  PASS

Result: 8/8 labs passed
```

## What it does

- Discovers the canonical labs deterministically (the `LAB-<nn>-<slug>` folders
  under `labs/`, in sorted order).
- Runs each lab's `config.yaml` through the existing agent/runner/evaluator
  stack.
- Compares the result against the lab's **declared** observations; it does not
  invent new ones.

## Options

| Flag | Meaning |
|---|---|
| (none) | Run the check for every canonical lab and print a PASS/FAIL summary. |
| `--json` | Emit the same report as JSON. |
| `--labs-dir <path>` | Point at a different labs directory (default: `labs`). |

## Behaviour

- It writes to a **temporary** directory, so it never touches `runs/` and never
  changes the lab definitions.
- It is fully **offline**: no network, no API keys, no model provider, no
  database.
- If any lab fails it prints a short reason (for example
  `tool_requests expected 99 got 1`) and the command returns a **non-zero** exit
  code, so it can gate automation.

## What it is — and is not

This is a **reproducibility / teaching check**: it confirms that the
deterministic educational scenarios still produce the observations they declare.

It is **not** a benchmark or a security score, and it says nothing about whether
the system is "secure", whether policies are "effective", whether any attack
"succeeds", or how a real model behaves. The deterministic fixture demonstrates
the mechanics of a security boundary, not real LLM behaviour.

CI runs the test suite and then this command, so a change that breaks a canonical
lab scenario fails the build.
