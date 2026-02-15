# coherence-stability-kernel

Runtime stability framework for agentic AI systems. Monitors five risk signals, aggregates them into a composite metric, and enforces regime-based operational limits.

## Quickstart

```bash
# Clone
git clone https://github.com/YOUR_ORG/coherence-stability-kernel.git
cd coherence-stability-kernel

# Run tests (standard library)
python -m unittest discover -s tests -v

# Run simulation
python sim/sim_stability.py
# Output: data/sim_output/stability.csv
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
│   └── test_kernel.py     # Unit tests for regime transitions, enforcement
├── docs/
│   ├── stability_theorem.md   # Formal stability condition
│   ├── simulation_spec.md     # Simulation inputs/outputs/invariants
│   └── whitepaper_draft.md    # Structured research paper draft
├── .github/workflows/
│   └── ci.yml             # CI: tests on Ubuntu + Windows
├── README.md
├── LICENSE                # MIT
└── .gitignore
```

## Risk Signals

| Signal | Measures | Source |
|--------|----------|--------|
| Φ₁ | Constraint violation accumulation | `ConstraintViolation` events |
| Φ₂ | Context divergence from session centroid | Prompt edit distance |
| Φ₃ | Tool integration instability | Circuit breaker OPEN ratio |
| Φ₄ | Retry storm pressure | Retries / requests ratio |
| Φ₅ | Recovery degradation | Time since last breaker reset |

## Regimes

| Regime | Φ_risk | Action |
|--------|--------|--------|
| STABLE | < 0.20 | Normal operation |
| PRESSURE | 0.20–0.50 | Scaled backoff (1.5×), reduced concurrency (70%) |
| UNSTABLE | 0.50–0.80 | Load shedding (LOW/NORMAL rejected), concurrency at 30% |
| FAILURE | ≥ 0.80 | SystemHalt, panic log written |

## Integration

```python
from src.kernel import CoherenceKernel
from src.regimes import Priority

kernel = CoherenceKernel()

# Pre-flight check (resilience layer)
snap = kernel.check_stability_preflight(priority=Priority.HIGH)

# Update signals (agent layer)
kernel.update_context_drift(0.3)
kernel.record_constraint_violation()
kernel.update_tool_instability(0.5)
```

## Safe Disclosure Mode

This repository supports two publication modes:

- **PUBLIC MODE** (default): Full kernel implementation, simulation, and tests are included.
- **SAFE MODE**: Replace `src/kernel.py` with `src/kernel_stub.py` (API surface only, no internal logic). Keep `src/metrics.py` and `src/regimes.py` as-is.

To toggle:
1. Copy `src/kernel.py` to `src/kernel_private.py` (keep locally).
2. Replace `src/kernel.py` with a stub that exposes the same public API but raises `NotImplementedError` for internal methods.
3. Add `src/kernel_private.py` to `.gitignore`.

## Dependencies

Python 3.10+ standard library only.

## License

MIT. See [LICENSE](LICENSE).
