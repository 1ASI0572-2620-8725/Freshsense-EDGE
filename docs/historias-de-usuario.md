# Historias de usuario — Freshsense-EDGE

Contexto: **iot_ingestion**. Fuente de verdad del hardware:
[Embebed-System](https://github.com/1ASI0572-2620-8725/Embebed-System).

## US-EDGE-01 — Ingesta del prototipo físico

**Como** ESP32 FreshSense  
**quiero** enviar `SensorReading` con temperatura, humedad y etileno  
**para** que el Edge clasifique la cámara de frío.

**Criterios**
- `POST /api/v1/sensor-readings` (ruta del firmware) y `POST /edge/process`.
- Campos: `temperatureC`/`temperature`, `humidityPct`/`humidity`, `ethylenePpm`, `timestamp`/`time`, `meta`.
- Respuesta `202` con `freshness` y `freshnessEmbedded` (FRESH / AT_RISK / SPOILED).

## US-EDGE-02 — Clasificar frescura FS-FRUIT-1

**Como** operador  
**quiero** semáforo GREEN / YELLOW / RED con tres ejes  
**para** alinearme al LED/ventilador del embebido.

**Criterios**
- Frutas: 0–8 °C, 90–95 %, 0–1 ppm.
- Manda el peor eje.
- Device UUID del firmware queda mapeado a Frutas.

## US-EDGE-03 — Reenvío al backend

**Como** plataforma FreshSense  
**quiero** reenviar la lectura ya clasificada  
**para** no perder datos si el backend falla momentáneamente.

**Criterios**
- Payload con `ethylenePpm`, `status`, `freshnessEmbedded`.
- Fallo upstream → `forwarded: false`, sin romper al ESP32.

## US-EDGE-04 — Claim / setup

**Como** instalador  
**quiero** vincular el Edge con un código  
**para** asociar secretos y categoría.

## US-EDGE-05 — Umbrales y devices

**Como** admin  
**quiero** listar umbrales (con etileno) y asignar categorías  
**para** soportar más dispositivos.
