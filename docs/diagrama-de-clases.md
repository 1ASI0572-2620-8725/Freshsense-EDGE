# Diagrama de clases — Freshsense-EDGE

Aplicación edge del bounded context **iot_ingestion**, en capas DDD. Recibe la lectura del nodo embebido ([Embebed-System](https://github.com/1ASI0572-2620-8725/Embebed-System)): temperatura, humedad y **etileno** (`ethylenePpm` del MQ135).

Equivalencia con el embebido FS-FRUIT-1:

| Edge | Embebido |
|---|---|
| GREEN | FRESH |
| YELLOW | AT_RISK |
| RED | SPOILED |

## Capas DDD

| Capa | Carpeta | Responsabilidad |
|---|---|---|
| Domain | `src/iot_ingestion/domain` | Entidades y reglas puras: `SensorReading`, `CategoryThreshold`, `classify` |
| Application | `src/iot_ingestion/application` | Casos de uso y puertos: `ProcessReading`, `ClaimDevice`, `validation`, `ports` |
| Infrastructure | `src/iot_ingestion/infrastructure` | Adaptadores: MySQL, memoria, HTTP al backend |
| Interfaces | `src/iot_ingestion/interfaces` | API Flask: `POST /edge/process`, umbrales, devices, claim |

El dominio no importa infraestructura ni Flask.

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
  }

  class classify {
    <<function>>
    +classify(temp, humidity, ethylene, threshold) FreshnessStatus
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
    +category_for_device(id)
    +threshold_for_category(cat)
  }

  class UpstreamForwarder {
    <<port>>
    +forward(reading, category, status, secret)
  }

  class InMemoryReadingRepository
  class MySqlThresholdCatalog
  class InMemoryThresholdCatalog
  class BackendForwarder
  class FlaskRoutes {
    +POST /edge/process
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

## Flujo

1. El ESP32 (Embebed) envía `deviceId`, temperatura, humedad, `ethylenePpm` y tiempo.
2. `validation` acepta alias del embebido (`temperatureC`, `humidityPct`, `timestamp` ISO).
3. `ProcessReading` guarda la lectura, busca la categoría (p. ej. Frutas) y llama a `classify` con **tres ejes**.
4. Responde `202` con `freshness` y reenvía al backend (best-effort).

## Frutas (FS-FRUIT-1)

Semilla por defecto: temp 0–8 °C, humedad 90–95 %, etileno 0–1 ppm. Dispositivo demo `esp32-freshsense-1` → Frutas.
