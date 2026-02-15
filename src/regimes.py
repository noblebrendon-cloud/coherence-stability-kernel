# src/regimes.py
from enum import Enum

class Regime(str, Enum):
    STABLE = "STABLE"
    PRESSURE = "PRESSURE"
    UNSTABLE = "UNSTABLE"
    FAILURE = "FAILURE"

class Priority(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    NORMAL = "NORMAL"
    LOW = "LOW"
