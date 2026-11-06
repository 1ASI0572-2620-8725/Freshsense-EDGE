# Freshsense-EDGE

Edge IoT de FreshSense en **DDD**. Recibe las lecturas del prototipo físico
([Embebed-System](https://github.com/1ASI0572-2620-8725/Embebed-System)):
temperatura, humedad y **etileno**, las clasifica en local y puede reenviarlas al backend.

## Documentación

| Archivo | Contenido |
|---|---|
| [docs/diagrama-de-clases.md](docs/diagrama-de-clases.md) | Capas DDD + Mermaid + secuencia ESP32 |
| [docs/class-diagram.puml](docs/class-diagram.puml) | PlantUML |
| [docs/historias-de-usuario.md](docs/historias-de-usuario.md) | Historias del contexto |

## Cómo habla el ESP32 real

El firmware hace `POST` a:

`http://<IP-DE-TU-PC>:5000/api/v1/sensor-readings`

con el JSON de Embebed:

```json
{
  "deviceId": "00000000-0000-0000-0000-000000000001",
  "timestamp": "2026-10-28T23:40:00",
  "temperatureC": 6.4,
  "humidityPct": 92.0,
  "ethylenePpm": 0.5,
  "meta": "firmware=1.0;origen=sensores"
}
```

También existe `POST /edge/process` (mismo caso de uso).

| Edge | Embebed |
|---|---|
| GREEN | FRESH |
| YELLOW | AT_RISK |
| RED | SPOILED |

## Arquitectura DDD

- **domain** — `SensorReading` (+ etileno + meta), `classify` a 3 ejes
- **application** — `ProcessReading`, `ClaimDevice`, validación con alias del embebido
- **infrastructure** — MySQL / memoria, forwarder HTTP
- **interfaces** — Flask

## Instalación y arranque

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
flask --app src.app run --host 0.0.0.0 --port 5000
```

`--host 0.0.0.0` permite que el ESP32 en la misma WiFi llegue a tu PC.

## Configuración

| Variable | Por defecto |
|---|---|
| `FRESHSENSE_BACKEND_URL` | `http://localhost:8080/api/edge/readings` |
| `FRESHSENSE_DB_HOST` | `localhost` (vacío = solo memoria) |

## Prueba rápida (payload embebido)

```bash
curl -X POST http://localhost:5000/api/v1/sensor-readings \
  -H "Content-Type: application/json" \
  -H "X-Device-Token: replace-with-device-token" \
  -d "{\"deviceId\":\"00000000-0000-0000-0000-000000000001\",\"timestamp\":\"2026-10-28T23:40:00\",\"temperatureC\":6.4,\"humidityPct\":92,\"ethylenePpm\":0.5,\"meta\":\"firmware=1.0\"}"
```

## Pruebas

```bash
pytest
```

## Embebido

En `FreshSenseNode.h` del Embebed-System, `READINGS_URL` debe apuntar a este Edge
(`http://IP:5000/api/v1/sensor-readings`) y el WiFi de la placa debe ser el de tu red.
