from __future__ import annotations

from src.iot_ingestion.domain.freshness import CategoryThreshold, FreshnessStatus, classify

# Frutas FS-FRUIT-1: 0–8 °C / 90–95 % / 0–1 ppm
FRUTAS = CategoryThreshold("Frutas", 0, 8, 90, 95, 0, 1)

# Lácteos: 1–5 °C / 70–85 % / 0–10 ppm
LACTEOS = CategoryThreshold("Lácteos", 1, 5, 70, 85, 0, 10)


def test_green_when_all_axes_in_range():
    assert classify(4, 80, 2, LACTEOS) is FreshnessStatus.GREEN


def test_green_frutas_with_low_ethylene():
    assert classify(6.4, 92, 0.5, FRUTAS) is FreshnessStatus.GREEN


def test_yellow_when_axis_is_near_the_limit():
    # 5.5 °C esta fuera del rango pero dentro del margen del 15% ((5-1)*0.15 = 0.6).
    assert classify(5.5, 80, 2, LACTEOS) is FreshnessStatus.YELLOW


def test_red_when_an_axis_is_far_out_of_range():
    assert classify(24, 80, 2, LACTEOS) is FreshnessStatus.RED


def test_worst_axis_wins_on_humidity():
    assert classify(4, 40, 2, LACTEOS) is FreshnessStatus.RED


def test_red_when_ethylene_is_far_out_for_frutas():
    # 5 ppm esta muy por encima de 1 ppm -> ROJO aunque temp/hum esten bien.
    assert classify(6.4, 92, 5, FRUTAS) is FreshnessStatus.RED


def test_yellow_when_ethylene_is_near_frutas_limit():
    # Margen etileno: (1-0)*0.15 = 0.15 -> 1.1 ppm es YELLOW.
    assert classify(6.4, 92, 1.1, FRUTAS) is FreshnessStatus.YELLOW
