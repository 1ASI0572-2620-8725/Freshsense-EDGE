from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class SensorReading:
    """Agregado de lectura IoT alineado al Embebed-System / informe 4.2.7.

    Campos del prototipo fisico (ESP32):
    deviceId, timestamp, temperatureC, humidityPct, ethylenePpm, meta.
    """

    device_id: str
    reading_id: str
    temperature: float
    humidity: float
    ethylene_ppm: float
    recorded_at: datetime
    meta: str = ""
