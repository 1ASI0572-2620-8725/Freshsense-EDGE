from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class FreshnessStatus(str, Enum):
    """Semaforo del Edge.

    Equivalencia con el embebido FS-FRUIT-1:
    GREEN -> FRESH, YELLOW -> AT_RISK, RED -> SPOILED.
    """

    GREEN = "GREEN"
    YELLOW = "YELLOW"
    RED = "RED"
    UNKNOWN = "UNKNOWN"

    def to_embedded_label(self) -> str:
        return {
            FreshnessStatus.GREEN: "FRESH",
            FreshnessStatus.YELLOW: "AT_RISK",
            FreshnessStatus.RED: "SPOILED",
            FreshnessStatus.UNKNOWN: "UNKNOWN",
        }[self]


@dataclass(frozen=True)
class CategoryThreshold:
    """Rango optimo por categoria (temp C, humedad %, etileno ppm)."""

    category: str
    temp_min: float
    temp_max: float
    humidity_min: float
    humidity_max: float
    ethylene_min: float
    ethylene_max: float


NEAR_MARGIN_RATIO = 0.15


def classify(
    temperature: float,
    humidity: float,
    ethylene_ppm: float,
    threshold: CategoryThreshold,
) -> FreshnessStatus:
    """Clasifica con el peor de tres ejes: temperatura, humedad y etileno."""
    return _worst(
        _axis_state(temperature, threshold.temp_min, threshold.temp_max),
        _axis_state(humidity, threshold.humidity_min, threshold.humidity_max),
        _axis_state(ethylene_ppm, threshold.ethylene_min, threshold.ethylene_max),
    )


class _AxisState(Enum):
    OK = 0
    NEAR = 1
    OUT = 2


def _axis_state(value: float, low: float, high: float) -> _AxisState:
    if low <= value <= high:
        return _AxisState.OK
    width = high - low
    margin = width * NEAR_MARGIN_RATIO if width > 0 else 0.0
    if (low - margin) <= value < low or high < value <= (high + margin):
        return _AxisState.NEAR
    return _AxisState.OUT


def _worst(a: _AxisState, b: _AxisState, c: _AxisState) -> FreshnessStatus:
    worst = max(a.value, b.value, c.value)
    if worst == _AxisState.OK.value:
        return FreshnessStatus.GREEN
    if worst == _AxisState.NEAR.value:
        return FreshnessStatus.YELLOW
    return FreshnessStatus.RED
