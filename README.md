# Freshsense-EDGE

Servicio edge IoT de FreshSense. Recibe lecturas del nodo embebido
([Embebed-System](https://github.com/1ASI0572-2620-8725/Embebed-System)):
**temperatura**, **humedad** y **etileno** (`ethylenePpm` del MQ135), las clasifica
en local (semáforo GREEN / YELLOW / RED) y las reenvía al backend.

Organización: [1ASI0572-2620-8725](https://github.com/1ASI0572-2620-8725)

## Documentación DDD

| Archivo | Contenido |
|---|---|
| [docs/diagrama-de-clases.md](docs/diagrama-de-clases.md) | Capas DDD y Mermaid |
| [docs/class-diagram.puml](docs/class-diagram.puml) | Mismo diagrama en PlantUML |
| [docs/historias-de-usuario.md](docs/historias-de-usuario.md) | Historias del contexto `iot_ingestion` |

## Arquitectura

Un contexto acotado (`iot_ingestion`) dividido en:

- **domain** — `SensorReading` (incluye `ethylene_ppm`) y `freshness`
  (`FreshnessStatus`, `CategoryThreshold` con rangos de etileno, `classify` a tres ejes).
- **application** — `validation`, `process_reading`, `claim_device`, `ports`.
- **infrastructure** — repositorio en memoria, MySQL local, forwarder HTTP, seed.
- **interfaces** — Flask: `POST /edge/process`, umbrales, devices, claim, setup.

El dominio no importa infraestructura ni interfaces.

### Semáforo y embebido

| Edge | Embebido FS-FRUIT-1 |
|---|---|
| GREEN | FRESH |
| YELLOW | AT_RISK |
| RED | SPOILED |

Semilla **Frutas** (alineada al embebido): 0–8 °C, 90–95 % humedad, 0–1 ppm etileno.
Dispositivo demo: `esp32-freshsense-1` → Frutas.

## Requisitos

- Python 3.10+
- MySQL 8.0 opcional (si no hay MySQL, catálogo en memoria).

## Instalación

```bash
python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Configuración

| Variable | Propósito | Por defecto |
|---|---|---|
| `FRESHSENSE_BACKEND_URL` | URL del backend | `http://localhost:8080/api/edge/readings` |
| `FRESHSENSE_FORWARD_TIMEOUT` | Timeout (s) | `5` |
| `FRESHSENSE_FORWARD_AUTH` | `X-Device-Key` de respaldo | _(vacío)_ |
| `FRESHSENSE_ENV` | `development` / `production` | `development` |
| `FRESHSENSE_DB_HOST` | MySQL | `localhost` |
| `FRESHSENSE_DB_PORT` | Puerto | `3306` |
| `FRESHSENSE_DB_USER` | Usuario | `root` |
| `FRESHSENSE_DB_PASSWORD` | Contraseña | `root` |
| `FRESHSENSE_DB_NAME` | Base | `freshsense_edge` |

## Ejecución

```bash
flask --app src.app run
```

## Endpoint principal

`POST /edge/process` — acepta el JSON del embebido (alias incluidos):

```bash
curl -X POST http://localhost:5000/edge/process \
  -H "Content-Type: application/json" \
  -d "{\"deviceId\":\"esp32-freshsense-1\",\"temperatureC\":6.4,\"humidityPct\":92,\"ethylenePpm\":0.5,\"timestamp\":\"2026-10-28T23:40:00\",\"id\":\"lectura-1\"}"
```

También acepta `temperature` / `humidity` / `time` (`dd/mm/yyyy HH:MM`).

Respuesta `202`:

```json
{
  "status": "ok",
  "forwarded": false,
  "category": "Frutas",
  "freshness": "GREEN",
  "reading": {
    "deviceId": "esp32-freshsense-1",
    "id": "lectura-1",
    "temperature": 6.4,
    "humidity": 92.0,
    "ethylenePpm": 0.5,
    "recordedAt": "2026-10-28T23:40:00"
  }
}
```

### Umbrales y dispositivos

```bash
curl http://localhost:5000/edge/thresholds
curl http://localhost:5000/edge/devices
curl -X POST http://localhost:5000/edge/devices \
  -H "Content-Type: application/json" \
  -d "{\"deviceId\":\"esp32-cocina\",\"category\":\"Frutas\"}"
```

## Pruebas

```bash
pytest
```
