# Historias de usuario — Freshsense-EDGE

Fuente de requisitos del producto:
[report](https://github.com/1ASI0572-2620-8725/report) §3.1 User Stories.

Este Edge implementa la **capa de borde** del epic **EP02 — Monitoreo IoT**
(y el contrato de ingesta **TS41**), recibiendo el prototipo físico
[Embebed-System](https://github.com/1ASI0572-2620-8725/Embebed-System)
(AM2302 + MQ135 → temperatura, humedad, etileno).

## Trazabilidad informe → Edge

| ID informe | Título | Qué hace el Edge |
|---|---|---|
| **US06** | Telemetría y monitoreo IoT de cámaras frías | Acepta lecturas temp/humedad/etileno del ESP32 |
| **US07** | Dashboard de inventario con semáforo | Clasifica GREEN / YELLOW / RED (y FRESH / AT_RISK / SPOILED) |
| **US08** | Alertas preventivas de temperatura | Emite estado crítico/amarillo para reenvío; sin falsa alarma en rango |
| **US31** | Vinculación y calibración de sensores | Claim/setup + mapeo device → categoría/umbrales |
| **TS41** | API Ingesta de Sensores IoT B2B | `POST /api/v1/sensor-readings` (mismo contrato del firmware) |

Historias de landing, inventario web, pagos, etc. (**US01–US05**, **US09–US30**, …)
viven en backend/front; aquí solo las que tocan el Edge + prototipo.

---

## US06 — Telemetría y monitoreo IoT de cámaras frías

**Como** propietario/administrador de restaurante o encargado de distribución en frío  
**quiero** que el sensor mida temperatura, humedad y etileno  
**para** enterarme antes de que el producto se malogre.

### Escenarios (del informe) → Edge

| Escenario | Criterio Edge |
|---|---|
| 1. Transmisión continua | `POST /api/v1/sensor-readings` con `temperatureC`, `humidityPct`, `ethylenePpm`, `timestamp`, `deviceId`, `meta` → `202` |
| 2. Pérdida de señal | El firmware envía heartbeat al backend; el Edge no inventa lecturas si no hay POST |
| 3. Lectura incompleta | Validación rechaza cuerpo sin temp/humedad/etileno/timestamp (`ValidationError`) |

**Contrato físico (Embebed `FreshSenseNode.h`):**

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

También: `POST /edge/process` (mismos campos / aliases legacy).

---

## US07 — Semáforo de frescura (Edge)

**Como** operador  
**quiero** verde / amarillo / rojo según la lectura  
**para** saber si la cámara está óptima, en riesgo o crítica.

### Escenarios → Edge

| Escenario | Criterio Edge |
|---|---|
| 1. Código de colores | `classify` a 3 ejes → `freshness`: GREEN / YELLOW / RED |
| 2. Detalle | Respuesta incluye `temperatureC`, `humidityPct`, `ethylenePpm`, `freshnessEmbedded` |
| 3. Sin lectura utilizable | Device sin categoría/umbral → `UNKNOWN` |

**Equivalencia prototipo FS-FRUIT-1**

| Edge | Embebido |
|---|---|
| GREEN | FRESH |
| YELLOW | AT_RISK |
| RED | SPOILED |

Umbral semilla **Frutas**: 0–8 °C, 90–95 %, 0–1 ppm.  
Devices: `esp32-freshsense-1`, `00000000-0000-0000-0000-000000000001`.

---

## US08 — Base de alertas preventivas (clasificación)

**Como** responsable del local  
**quiero** que un desvío de frío/humedad/etileno quede marcado  
**para** actuar antes de perder el producto.

### Escenarios → Edge

| Escenario | Criterio Edge |
|---|---|
| 1. Quiebre crítico | Peor eje OUT → RED / SPOILED; se reenvía `status` + `freshnessEmbedded` |
| 2. Sin falsas alarmas | Valores dentro de umbral → GREEN; no se fuerza alerta |
| 3. Fallo canal upstream | Forward best-effort: `forwarded: false`, el ESP32 igual recibe `202` |

El push/SMS lo resuelve el backend (**TS42**); el Edge aporta el estado ya clasificado.

---

## US31 — Vinculación de sensores (claim / categoría)

**Como** supervisor  
**quiero** vincular el dispositivo y asociar umbrales de la cámara  
**para** que cada zona use su calibración.

### Escenarios → Edge

| Escenario | Criterio Edge |
|---|---|
| 1. Vinculación | `POST /edge/claim` + página `/edge/setup` |
| 2. Umbral por categoría | `GET/POST /edge/devices`, `GET /edge/thresholds` (incl. etileno) |
| 3. Inválido | Código vacío / device ya owned → error de validación |

---

## TS41 — API Ingesta de Sensores IoT B2B

**Como** desarrollador del backend / Edge  
**quiero** recibir lecturas autenticables de temp/humedad/etileno  
**para** alimentar el panel.

### Escenarios → Edge

| Escenario | Criterio Edge |
|---|---|
| 1. Lectura aceptada | JSON válido → guarda en store local, clasifica, `202` (gateway Edge) |
| 2. Id de lectura | Si no viene `id`, se genera; si viene, se conserva |
| 3. Token | Header `X-Device-Token` aceptado del firmware; validación estricta 401 queda en backend cloud |

Ruta canónica del informe y del firmware:

`POST /api/v1/sensor-readings`

---

## Cobertura de código (DDD)

| Historia | Domain | Application | Infrastructure | Interfaces |
|---|---|---|---|---|
| US06 / TS41 | `SensorReading` | `validate_reading_request` | `InMemoryReadingRepository` | `/api/v1/sensor-readings` |
| US07 / US08 | `classify`, `FreshnessStatus` | `ProcessReading` | `BackendForwarder` | respuesta `freshness*` |
| US31 | `CategoryThreshold` | `ClaimDevice` | seed / MySQL catalog | `/edge/claim`, `/edge/devices` |
