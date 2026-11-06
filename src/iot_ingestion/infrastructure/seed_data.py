from __future__ import annotations

from src.iot_ingestion.domain.freshness import CategoryThreshold

# Umbrales de referencia por categoria (temp °C / humedad % / etileno ppm).
# Frutas sigue FS-FRUIT-1 del Embebed-System: 0–8 °C, 90–95 %, 0–1 ppm.
# Datos semilla; no dependen de ningun driver de BD para poder reutilizarse
# tambien en el catalogo en memoria (pruebas / fallback sin MySQL).
DEFAULT_THRESHOLDS: tuple[CategoryThreshold, ...] = (
    CategoryThreshold("Frutas", 0, 8, 90, 95, 0, 1),
    CategoryThreshold("Verduras", 0, 6, 90, 98, 0, 5),
    CategoryThreshold("Lácteos", 1, 5, 70, 85, 0, 10),
    CategoryThreshold("Carnes", -1, 4, 75, 85, 0, 10),
    CategoryThreshold("Proteínas", 0, 4, 75, 85, 0, 10),
    CategoryThreshold("Panadería", 16, 24, 50, 65, 0, 20),
    CategoryThreshold("Snacks", 16, 24, 40, 55, 0, 20),
)

# Dispositivos demo -> Frutas (camara de frio del Embebed-System).
DEFAULT_DEVICE_CATEGORIES: dict[str, str] = {
    "esp32-freshsense-1": "Frutas",
    # DEVICE_ID por defecto del firmware Embebed-System.
    "00000000-0000-0000-0000-000000000001": "Frutas",
}
