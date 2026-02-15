# Simulation Specification

## Objectives
Validate kernel regime transitions under synthetic load.

## Inputs
1.  **Duration**: 100 ticks (default).
2.  **Constraint Violations**: Random injection [0, 2] per tick (C1).
3.  **Tool Instability**: Linear ramp 0.0 -> 1.0 (C3).
4.  **Escalation Spike**: Burst of retries at t=60 (C4).

## Outputs
CSV file `data/sim_output/stability.csv` with columns:
-   `step`: Simulation tick
-   `ts`: Timestamp
-   `phi1`..`phi5`: Current risk metrics
-   `phi_risk`: Aggregated risk
-   `E`: Escalation ratio
-   `regime`: Current state (STABLE, PRESSURE, UNSTABLE, FAILURE)

## Invariants
1.  $\Phi_{risk}$ must monotonically increase if input noise is linear.
2.  $E$ must spike when $d\Phi/dt$ is high.
3.  Regime transitions must follow hysteresis rules.
