# Diagrama de clases — Freshsense-EDGE (DDD)

Bounded context **iot_ingestion** (informe:
[report](https://github.com/1ASI0572-2620-8725/report) — IoT Monitoring / EP02).

El Edge recibe las lecturas del prototipo físico
[Embebed-System](https://github.com/1ASI0572-2620-8725/Embebed-System)
(`AM2302` + `MQ135` → `temperatureC`, `humidityPct`, `ethylenePpm`)
por el contrato **TS41**: `POST /api/v1/sensor-readings`.

## Capas

| Capa | Carpeta | Piezas | Historias |
|---|---|---|---|
| Domain | `domain/` | `SensorReading`, `CategoryThreshold`, `FreshnessStatus`, `classify` | US06, US07, US08 |
| Application | `application/` | `ProcessReading`, `ClaimDevice`, `validation`, `ports` | US06, US31, TS41 |
| Infrastructure | `infrastructure/` | MySQL / memoria, `BackendForwarder`, claim HTTP | US08, US31 |
| Interfaces | `interfaces/` | Flask: `/edge/*` y `/api/v1/sensor-readings` | TS41, US31 |

## Dibujo

```mermaid
classDiagram
  direction TB

  class SensorReading {
    +device_id str
    +reading_id str
    +temperature float
    +humidity float
    +ethylene_ppm float
    +recorded_at datetime
    +meta str
  }

  class CategoryThreshold {
    +category str
    +temp_min float
    +temp_max float
    +humidity_min float
    +humidity_max float
    +ethylene_min float
    +ethylene_max float
  }

  class FreshnessStatus {
    <<enumeration>>
    GREEN
    YELLOW
    RED
    UNKNOWN
    +to_embedded_label() str
  }

  class classify {
    <<domain service>>
    +classify(temp, hum, ethylene, threshold) FreshnessStatus
  }

  class ProcessReading {
    +execute(validated) ProcessResult
  }

  class ClaimDevice {
    +execute(code) ClaimResult
  }

  class ReadingStore {
    <<port>>
    +add(reading)
  }

  class ThresholdCatalog {
    <<port>>
    +category_for_device()
    +threshold_for_category()
  }

  class UpstreamForwarder {
    <<port>>
    +forward()
  }

  class InMemoryReadingRepository
  class MySqlThresholdCatalog
  class InMemoryThresholdCatalog
  class BackendForwarder
  class FlaskRoutes {
    +POST /edge/process
    +POST /api/v1/sensor-readings
    +GET /edge/thresholds
    +POST /edge/claim
  }

  ProcessReading ..> SensorReading
  ProcessReading ..> classify
  ProcessReading ..> ReadingStore
  ProcessReading ..> ThresholdCatalog
  ProcessReading ..> UpstreamForwarder
  classify ..> CategoryThreshold
  classify ..> FreshnessStatus
  InMemoryReadingRepository ..|> ReadingStore
  MySqlThresholdCatalog ..|> ThresholdCatalog
  InMemoryThresholdCatalog ..|> ThresholdCatalog
  BackendForwarder ..|> UpstreamForwarder
  FlaskRoutes ..> ProcessReading
  FlaskRoutes ..> ClaimDevice
```

Versión PlantUML: [class-diagram.puml](class-diagram.puml).

## Flujo con el ESP32 real (US06 + TS41 + US07)

```mermaid
sequenceDiagram
  participant ESP as Embebed ESP32
  participant Edge as Freshsense-EDGE
  participant Dom as domain.classify
  participant BE as Backend

  ESP->>Edge: POST /api/v1/sensor-readings
  Note over ESP,Edge: temperatureC humidityPct ethylenePpm timestamp
  Edge->>Dom: classify 3 ejes (US07/US08)
  Dom-->>Edge: GREEN YELLOW o RED
  Edge-->>ESP: 202 freshness + freshnessEmbedded
  Edge->>BE: forward best-effort (TS41 upstream)
```

## Equivalencia con el embebido

| Edge | Embebed FS-FRUIT-1 | Informe |
|---|---|---|
| GREEN | FRESH | óptimo |
| YELLOW | AT_RISK | priorizar uso |
| RED | SPOILED | crítico |

Frutas (semilla): 0–8 °C, 90–95 %, 0–1 ppm.  
Devices: `esp32-freshsense-1` y `00000000-0000-0000-0000-000000000001`.
