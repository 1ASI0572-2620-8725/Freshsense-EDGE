# Historias de usuario — Freshsense-EDGE

Bounded context: **iot_ingestion**. El Edge recibe lecturas del nodo físico documentado en [Embebed-System](https://github.com/1ASI0572-2620-8725/Embebed-System) (AM2302 + MQ135, FS-FRUIT-1).

## US-EDGE-01 — Recibir lectura con etileno

**Como** dispositivo ESP32 FreshSense  
**quiero** enviar temperatura, humedad y etileno al Edge  
**para** que la cámara de frío quede registrada con las tres magnitudes del informe.

**Criterios**
- `POST /edge/process` acepta `temperature` / `temperatureC`, `humidity` / `humidityPct`, `ethylenePpm`.
- Acepta `time` (dd/mm/yyyy HH:MM) o `timestamp` ISO del embebido.
- Responde `202` con la lectura persistida en el cuerpo.

## US-EDGE-02 — Clasificar frescura (tres ejes)

**Como** operador de la cámara  
**quiero** un semáforo GREEN / YELLOW / RED según umbrales de categoría  
**para** saber si la fruta está FRESH, AT_RISK o SPOILED (equivalencia con el embebido).

**Criterios**
- Se usa la categoría del dispositivo (p. ej. Frutas).
- Se evalúan temperatura, humedad y etileno; manda el peor eje.
- Frutas sembrada: 0–8 °C, 90–95 %, 0–1 ppm (FS-FRUIT-1).

## US-EDGE-03 — Reenviar al backend

**Como** sistema FreshSense  
**quiero** que el Edge reenvíe la lectura clasificada al backend  
**para** centralizar el monitoreo sin bloquear al dispositivo si el backend falla.

**Criterios**
- El payload incluye `ethylenePpm` y `status`.
- Si el backend no responde, el Edge igual responde `202` con `forwarded: false`.

## US-EDGE-04 — Vincular dispositivo (claim)

**Como** usuario de la app  
**quiero** canjear un código de vinculación en el Edge  
**para** asociar el ESP32 a una categoría y guardar la clave local.

**Criterios**
- `POST /edge/claim` con `code`.
- Página `GET /edge/setup` para el flujo manual.

## US-EDGE-05 — Gestionar umbrales y categorías

**Como** administrador  
**quiero** listar umbrales y asignar categoría a un `deviceId`  
**para** clasificar lecturas de distintos tipos de alimento.

**Criterios**
- `GET /edge/thresholds` incluye rangos de etileno.
- `POST /edge/devices` exige una categoría que exista en el catálogo.

## Relación con el embebido

| Embebido | Edge |
|---|---|
| `SensorReading` con `ethylenePpm` | Mismo campo en dominio y API |
| LED ← temp/hum; ventilador ← etileno | Clasificación agregada en tres ejes |
| FRESH / AT_RISK / SPOILED | GREEN / YELLOW / RED |
