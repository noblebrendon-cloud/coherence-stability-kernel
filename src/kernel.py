# src/kernel.py
from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Dict, Optional, List, Any
import json
from pathlib import Path

from src.regimes import Regime, Priority
import src.metrics as m

class SystemHalt(Exception):
    pass

class LoadShed(Exception):
    pass

@dataclass
class KernelConfig:
    window_seconds: int = 60
    tick_seconds: int = 5
    lambda1: float = 0.5
    dmax: float = 0.4
    rmax: float = 3.0
    k: float = 0.1
    t_target: float = 300.0
    w_weights: Dict[str, float] = field(default_factory=lambda: {
        "phi1": 1.5, "phi2": 1.0, "phi3": 2.0, "phi4": 1.0, "phi5": 0.5
    })
    alpha: float = 0.2
    dphi_ticks: int = 3
    epsilon: float = 0.1
    K_stiffness: float = 1.0
    # Hysteresis
    stable_enter: float = 0.15
    pressure_enter: float = 0.20
    unstable_enter: float = 0.50
    failure_enter: float = 0.80
    pressure_exit_low: float = 0.15
    unstable_exit_low: float = 0.45

@dataclass
class KernelSnapshot:
    ts: float
    phi1: float
    phi2: float
    phi3: float
    phi4: float
    phi5: float
    phi_risk: float
    coherence: float
    A: float
    R: float
    E: float
    regime: Regime

class CoherenceKernel:
    def __init__(self, cfg: Optional[KernelConfig] = None):
        self.cfg = cfg or KernelConfig()
        self._slots = max(1, self.cfg.window_seconds // self.cfg.tick_seconds)
        self._idx = 0
        self._tick_ts = time.time()
        
        self._violations = [0] * self._slots
        self._requests = [0] * self._slots
        self._retries = [0] * self._slots
        
        self._phi2 = 0.0
        self._phi3 = 0.0
        self._last_reset_ts = time.time()
        self._regime = Regime.STABLE
        self._phi_hist = []  # list[(ts, phi_risk)]

    def tick(self, now: Optional[float] = None) -> None:
        now = now or time.time()
        if now - self._tick_ts < self.cfg.tick_seconds:
            return
        steps = int((now - self._tick_ts) // self.cfg.tick_seconds)
        for _ in range(steps):
            self._idx = (self._idx + 1) % self._slots
            self._violations[self._idx] = 0
            self._requests[self._idx] = 0
            self._retries[self._idx] = 0
            self._tick_ts += self.cfg.tick_seconds

    # Event Ingestion
    def record_constraint_violation(self, count: int = 1):
        self._violations[self._idx] += max(0, int(count))

    def record_request(self, retries: int = 0):
        self._requests[self._idx] += 1
        self._retries[self._idx] += max(0, int(retries))

    def update_context_drift(self, drift: float):
        self._phi2 = m.compute_phi2(drift, self.cfg.dmax)

    def update_tool_instability(self, open_ratio: float):
        self._phi3 = m.compute_phi3(open_ratio)

    def record_breaker_reset(self):
        self._last_reset_ts = time.time()

    # Kernel Logic
    def snapshot(self, now: Optional[float] = None) -> KernelSnapshot:
        now = now or time.time()
        self.tick(now)

        # Compute Phis
        vc = sum(self._violations)
        req = sum(self._requests)
        ret = sum(self._retries)
        t_last = max(0.0, now - self._last_reset_ts)

        phi1 = m.compute_phi1(vc, self.cfg.lambda1)
        phi2 = self._phi2
        phi3 = self._phi3
        phi4 = m.compute_phi4(ret, req, self.cfg.rmax)
        phi5 = m.compute_phi5(t_last, self.cfg.t_target, self.cfg.k)

        phis = {"phi1":phi1, "phi2":phi2, "phi3":phi3, "phi4":phi4, "phi5":phi5}
        phi_risk = m.aggregate_risk(phis, self.cfg.w_weights, self.cfg.alpha)
        
        # Escalation
        self._phi_hist.append((now, phi_risk))
        hist_len = max(20, self.cfg.dphi_ticks + 2)
        if len(self._phi_hist) > hist_len:
            self._phi_hist = self._phi_hist[-hist_len:]
        
        A = 0.0
        if len(self._phi_hist) >= (self.cfg.dphi_ticks + 1):
            t0, p0 = self._phi_hist[-(self.cfg.dphi_ticks + 1)]
            t1, p1 = self._phi_hist[-1]
            dt = max(1e-9, t1 - t0)
            A = max(0.0, (p1 - p0) / dt)

        R_cap = 1.0 - phi3
        E = A / (R_cap + self.cfg.epsilon)
        
        # Hysteresis
        self._regime = self._update_regime(phi_risk)
        
        return KernelSnapshot(now, phi1, phi2, phi3, phi4, phi5, phi_risk, 1.0-phi_risk, A, R_cap, E, self._regime)

    def _update_regime(self, p: float) -> Regime:
        r = self._regime
        if r == Regime.FAILURE: return Regime.FAILURE
        
        # FAILURE
        if p >= self.cfg.failure_enter: return Regime.FAILURE
        
        # UNSTABLE
        if r == Regime.UNSTABLE:
            if p < self.cfg.unstable_exit_low: return Regime.PRESSURE
            return Regime.UNSTABLE
        
        # PRESSURE
        if r == Regime.PRESSURE:
            if p >= self.cfg.unstable_enter: return Regime.UNSTABLE
            if p < self.cfg.pressure_exit_low: return Regime.STABLE
            return Regime.PRESSURE
        
        # STABLE
        if p >= self.cfg.pressure_enter: return Regime.PRESSURE
        return Regime.STABLE

    # Enforcement Hooks
    def check_stability_preflight(self, priority: Priority = Priority.LOW):
        snap = self.snapshot()
        
        if snap.regime == Regime.FAILURE:
            self._persist_panic(snap)
            raise SystemHalt("Coherence Collapse")
            
        if snap.regime == Regime.UNSTABLE:
            if priority in (Priority.LOW, Priority.NORMAL):
                raise LoadShed("Shedding Low Priority")
        
        return snap

    def _persist_panic(self, snap: KernelSnapshot):
        try:
            Path("data/state").mkdir(parents=True, exist_ok=True)
            with open("data/state/panic.log", "a") as f:
                f.write(json.dumps({
                    "ts": snap.ts, "regime": snap.regime.value, 
                    "phi_risk": snap.phi_risk, "E": snap.E
                }) + "\n")
        except:
            pass
