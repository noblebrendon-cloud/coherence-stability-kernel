# coherence-stability-kernel

Runtime stability framework for agentic AI systems operating under real-world pressure.

> Converts distributed runtime instability into enforceable operational boundaries.

---

## Why This Exists

Agentic systems degrade gradually before failing catastrophically. In production, minor errors—constraint violations, context drift, tool instability, and retry amplification—compound into systemic failure.

The coherence-stability-kernel models runtime health through five independent failure channels (Φ₁–Φ₅), aggregates them into a composite stability score (Φ_risk), and enforces deterministic regime transitions:

**STABLE → PRESSURE → UNSTABLE → FAILURE**

Designed for:

- Founders deploying AI into production
- Operators responsible for runtime reliability
- Engineers building governance layers
- Consultants implementing AI safeguards

---

## Quickstart

```bash
# Clone
git clone https://github.com/YOUR_ORG/coherence-stability-kernel.git
cd coherence-stability-kernel

# Run tests
python -m unittest discover -s tests -v

# Run simulation
python sim/sim_stability.py
# Output: data/sim_output/stability.csv

## Repository Structure
```

## Repository Structure

```
coherence-stability-kernel/
├── src/
│   ├── __init__.py
│   ├── kernel.py          # CoherenceKernel class, enforcement hooks
│   ├── metrics.py         # Φ₁–Φ₅ normalization functions, aggregation
│   └── regimes.py         # Regime and Priority enums
├── sim/
│   └── sim_stability.py   # Fault-injection simulation harness
├── tests/
│   └── test_kernel.py     # Unit tests for regime transitions
├── docs/
│   ├── stability_theorem.md
│   ├── simulation_spec.md
│   └── whitepaper_draft.md
├── .github/workflows/
│   └── ci.yml             # CI: tests on Ubuntu + Windows
├── README.md
├── LICENSE
└── .gitignore

| Signal | Measures                                 | Source                        |
| ------ | ---------------------------------------- | ----------------------------- |
| Φ₁     | Constraint violation accumulation        | `ConstraintViolation` events  |
| Φ₂     | Context divergence from session centroid | Prompt edit distance          |
| Φ₃     | Tool integration instability             | Circuit breaker OPEN ratio    |
| Φ₄     | Retry storm pressure                     | Retries / requests ratio      |
| Φ₅     | Recovery degradation                     | Time since last breaker reset |

| Regime   | Φ_risk    | Enforcement                               |
| -------- | --------- | ----------------------------------------- |
| STABLE   | < 0.20    | Normal operation                          |
| PRESSURE | 0.20–0.50 | Backoff (1.5×), reduced concurrency (70%) |
| UNSTABLE | 0.50–0.80 | Load shedding, concurrency at 30%         |
| FAILURE  | ≥ 0.80    | System halt + panic log                   |

from src.kernel import CoherenceKernel
from src.regimes import Priority

kernel = CoherenceKernel()
snap = kernel.check_stability_preflight(priority=Priority.HIGH)

kernel.update_context_drift(0.3)
kernel.record_constraint_violation()
kernel.update_tool_instability(0.5)

Safe Disclosure Mode

This repository supports two publication modes:

PUBLIC MODE — Full kernel implementation, simulation, and tests included.

SAFE MODE — Replace src/kernel.py with src/kernel_stub.py (API surface only).

To toggle:

Copy src/kernel.py to src/kernel_private.py

Replace src/kernel.py with stub

Add src/kernel_private.py to .gitignore

Dependencies

Python 3.10+ standard library only.

Author: Brendan R. Coleman
Primary site: https://brendonrcoleman.com

License

MIT. See LICENSE.
