# src/metrics.py
import math

def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return lo if x < lo else hi if x > hi else x

def sigmoid(x: float) -> float:
    # σ(x) = 1/(1+e^-x)
    try:
        return 1.0 / (1.0 + math.exp(-x))
    except OverflowError:
        return 0.0 if x < 0 else 1.0

def compute_phi1(violations: int, lambda1: float) -> float:
    # C1: 1 - exp(-lambda1 * violations)
    return 1.0 - math.exp(-lambda1 * float(violations))

def compute_phi2(drift: float, dmax: float) -> float:
    # C2: clamp(drift / dmax, 0, 1)
    return clamp(drift / max(dmax, 1e-9), 0.0, 1.0)

def compute_phi3(open_ratio: float) -> float:
    # C3: clamp(open_ratio, 0, 1)
    return clamp(open_ratio, 0.0, 1.0)

def compute_phi4(retries: int, requests: int, rmax: float) -> float:
    # C4: clamp((retries/requests)/rmax, 0, 1)
    if requests <= 0:
        return 0.0
    rate = float(retries) / float(requests)
    return clamp(rate / max(rmax, 1e-9), 0.0, 1.0)

def compute_phi5(last_reset_age: float, target: float, k: float) -> float:
    # C5: sigmoid(k * (age - target))
    return sigmoid(k * (last_reset_age - target))

def aggregate_risk(phis: dict, weights: dict, alpha: float) -> float:
    w_sum = sum(weights.values())
    w_avg = sum(weights[k] * phis[k] for k in weights) / max(w_sum, 1e-9)
    worst = max(phis.values())
    return clamp((1.0 - alpha) * w_avg + alpha * worst)
