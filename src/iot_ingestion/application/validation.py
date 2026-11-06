from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from src.shared.errors import ValidationError

TEMP_MIN, TEMP_MAX = -40.0, 85.0
HUMIDITY_MIN, HUMIDITY_MAX = 0.0, 100.0
ETHYLENE_MIN, ETHYLENE_MAX = 0.0, 10000.0
TIME_FORMAT = "%d/%m/%Y %H:%M"


@dataclass(frozen=True)
class ValidatedReading:
    device_id: str
    reading_id: str
    temperature: float
    humidity: float
    ethylene_ppm: float
    recorded_at: datetime


def validate_reading_request(body: Any) -> ValidatedReading:
    if not isinstance(body, dict):
        raise ValidationError("El cuerpo de la peticion debe ser un objeto JSON")
    return ValidatedReading(
        device_id=_require_str(body, "deviceId"),
        reading_id=_optional_reading_id(body),
        temperature=_require_number(
            body, "temperature", TEMP_MIN, TEMP_MAX, aliases=("temperatureC",)
        ),
        humidity=_require_number(
            body, "humidity", HUMIDITY_MIN, HUMIDITY_MAX, aliases=("humidityPct",)
        ),
        ethylene_ppm=_require_number(
            body, "ethylenePpm", ETHYLENE_MIN, ETHYLENE_MAX, aliases=("ethylene_ppm",)
        ),
        recorded_at=_require_timestamp(body),
    )


def _optional_reading_id(body: dict[str, Any]) -> str:
    value = body.get("id")
    if isinstance(value, str) and value.strip():
        return value.strip()
    return uuid.uuid4().hex[:20]


def _require_str(body: dict[str, Any], field: str) -> str:
    value = body.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{field} es obligatorio y debe ser un texto no vacio")
    return value


def _require_number(
    body: dict[str, Any],
    field: str,
    low: float,
    high: float,
    aliases: tuple[str, ...] = (),
) -> float:
    value = body.get(field)
    used = field
    if value is None:
        for alias in aliases:
            if body.get(alias) is not None:
                value = body.get(alias)
                used = alias
                break
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValidationError(f"{used} es obligatorio y debe ser un numero")
    if not low <= float(value) <= high:
        raise ValidationError(f"{used} debe estar entre {low} y {high}")
    return float(value)


def _require_timestamp(body: dict[str, Any]) -> datetime:
    # Embebido: timestamp ISO. Edge legacy: time dd/mm/yyyy HH:MM.
    if "time" in body and body.get("time") is not None:
        value = body.get("time")
        if not isinstance(value, str):
            raise ValidationError(f"time es obligatorio y debe ser un texto con formato {TIME_FORMAT}")
        try:
            return datetime.strptime(value, TIME_FORMAT)
        except ValueError as exc:
            raise ValidationError(f"time debe tener el formato {TIME_FORMAT}") from exc

    value = body.get("timestamp")
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(
            f"time ({TIME_FORMAT}) o timestamp (ISO) es obligatorio"
        )
    text = value.strip().replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(text)
    except ValueError as exc:
        raise ValidationError("timestamp debe ser una fecha ISO valida") from exc
