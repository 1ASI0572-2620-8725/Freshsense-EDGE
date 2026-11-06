# Diagrama de clases — Freshsense-EDGE (DDD)

Bounded context **iot_ingestion**. El Edge recibe las lecturas del prototipo físico
[Embebed-System](https://github.com/1ASI0572-2620-8725/Embebed-System)
(`AM2302` + `MQ135` → `temperatureC`, `humidityPct`, `ethylenePpm`).

## Capas

| Capa | Carpeta | Piezas |
|---|---|---|
| Domain | `domain/` | `SensorReading`, `CategoryThreshold`, `FreshnessStatus`, `classify` |
| Application | `application/` | `ProcessReading`, `ClaimDevice`, `validation`, `ports` |
| Infrastructure | `infrastructure/` | MySQL, memoria, `BackendForwarder`, claim HTTP |
| Interfaces | `interfaces/` | Flask: `/edge/process` y `/api/v1/sensor-readings` |

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

## Flujo con el ESP32 real

```mermaid
sequenceDiagram
  participant ESP as Embebed ESP32
  participant Edge as Freshsense-EDGE
  participant Dom as domain.classify
  participant BE as Backend

  ESP->>Edge: POST /api/v1/sensor-readings
  Note over ESP,Edge: temperatureC humidityPct ethylenePpm timestamp
  Edge->>Dom: classify 3 ejes
  Dom-->>Edge: GREEN YELLOW o RED
  Edge-->>ESP: 202 freshness + freshnessEmbedded
  Edge->>BE: forward best-effort
```

## Equivalencia con el embebido

| Edge | Embebed FS-FRUIT-1 |
|---|---|
| GREEN | FRESH |
| YELLOW | AT_RISK |
| RED | SPOILED |

Frutas (semilla): 0–8 °C, 90–95 %, 0–1 ppm.  
Devices sembrados: `esp32-freshsense-1` y `00000000-0000-0000-0000-000000000001`.
