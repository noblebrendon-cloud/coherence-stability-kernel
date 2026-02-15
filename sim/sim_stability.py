# sim/sim_stability.py
import sys
import time
import random
import csv
from pathlib import Path

# Add repo root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.kernel import CoherenceKernel, Regime

def run_sim(duration_steps=100):
    kernel = CoherenceKernel()
    
    Path("data/sim_output").mkdir(parents=True, exist_ok=True)
    csv_file = Path("data/sim_output/stability.csv")
    
    with open(csv_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["step", "ts", "phi1", "phi2", "phi3", "phi4", "phi5", "phi_risk", "E", "regime"])
        
        print(f"Starting simulation for {duration_steps} steps...")
        
        for step in range(duration_steps):
            # 0-30: Stable
            # 30-60: Degrading (C1 violations, C3 breakers)
            # 60-80: Critical (C4 retries spike)
            # 80+: Recovery or Failure
            
            if step > 30:
                kernel.record_constraint_violation(random.randint(0, 2))
                kernel.update_tool_instability(min(1.0, (step - 30) * 0.02))
            
            if step > 60:
                kernel.record_request(retries=random.randint(1, 4))
            else:
                kernel.record_request(retries=0)
                
            snap = kernel.snapshot()
            
            writer.writerow([
                step, snap.ts, 
                f"{snap.phi1:.2f}", f"{snap.phi2:.2f}", f"{snap.phi3:.2f}", 
                f"{snap.phi4:.2f}", f"{snap.phi5:.2f}", 
                f"{snap.phi_risk:.2f}", f"{snap.E:.2f}", 
                snap.regime.value
            ])
            
            if step % 10 == 0:
                print(f"Step {step}: Regime={snap.regime.value} Risk={snap.phi_risk:.2f}")

    print(f"Simulation complete. Output: {csv_file}")

if __name__ == "__main__":
    run_sim()
