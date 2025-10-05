# 📱 Comandos del Bot APRS

## Comandos Básicos

### `/start`
Muestra mensaje de bienvenida y lista de comandos disponibles.

### `/help`
Muestra ayuda con todos los comandos disponibles.

---

## Comandos de Consulta APRS

### `/info <indicativo>` ⭐ NUEVO
Muestra información completa de una estación desde TrackDirect.

**Ejemplo:** `/info LU1QA-1`

**Muestra:**
- 📍 Última posición (latitud, longitud, altitud)
- 🚗 Movimiento (velocidad, rumbo)
- 🕐 Timestamp con "hace cuánto tiempo"
- 💬 Último comentario/status
- 📊 Estadísticas (total packets, días activo, primera escucha)
- 🎯 Tipo de estación (móvil, fija, WX, etc.)

**Formato de salida:**
```
📡 LU1QA-1 🚗

📍 Posición
├─ Lat: -34.6037°
└─ Lon: -58.3816°

🏔️ Altitud: 25 m

🚗 Movimiento
├─ Velocidad: 65 km/h 🚗
└─ Rumbo: 45° NE

🕐 Última actualización
├─ 05/10/2025 17:45:30 ART
└─ hace 3 minutos

💬 Comentario
└─ En ruta a La Plata

📊 Estadísticas
├─ Packets totales: 1,247
├─ Días activo: 45
└─ Primera escucha: 20/08/2025 10:15:00 ART
```

---

### `/telemetria <indicativo>` ⭐ MEJORADO
Muestra telemetría completa con históricos y tendencias desde TrackDirect.

**Ejemplo:** `/telemetria LU1QA-1`

**Muestra:**
- 🔋 Voltaje de batería con barra de progreso
- 🌡️ Temperatura con indicador
- 📡 Señal RSSI
- 💾 Estados digitales (GPS Fix, TX, Low Power, etc.)
- 📈 Tendencias de las últimas 24 horas
- 📊 Secuencia de paquetes

**Formato de salida:**
```
📊 Telemetría LU1QA-1

🔋 Alimentación
├─ Batería: 13.2V ━━━━━━━━━━ 88%
└─ Panel solar: 5.1V ☀️

🌡️ Sensores
├─ Temperatura: 24.5°C ☀️
└─ Señal RSSI: -72 dBm ━━━━━─── 65% 📡

💾 Sistema
├─ ✅ GPS Lock
├─ ✅ TX ON
└─ ⚡ Normal Power

📈 Tendencia (últimas 24h)
├─ Batería: 13.2 → 13.0 → 12.8 → 13.2 ↗️
└─ Temp: 22.0 → 24.0 → 26.0 → 24.5 →

📡 Última actualización
├─ Secuencia: #4,582
├─ 05/10/2025 17:45:30 ART
└─ hace 3 minutos
```

**Características:**
- ✅ Datos en tiempo real desde TrackDirect
- 📊 Histórico de 24 horas
- 📈 Gráficos de tendencias
- 🔋 Barras de progreso visuales
- ⚡ Emojis descriptivos para cada sensor

---

### `/aprs <indicativo>`
Última posición APRS (usa API de aprs.fi).

**Ejemplo:** `/aprs LU1QA-1`

**Muestra:**
- Latitud y longitud
- Hora del último reporte
- Comentario

---

### `/wx <indicativo>`
Datos meteorológicos de estaciones WX.

**Ejemplo:** `/wx LU1QA-13`

**Muestra:**
- Temperatura
- Humedad
- Velocidad del viento

---

### `/ssid <indicativo>`
Lista todos los SSID activos de un indicativo base.

**Ejemplo:** `/ssid LU1QA`

**Muestra:**
- Lista de todos los SSID vistos (LU1QA-1, LU1QA-5, etc.)

---

## Comandos de Administrador

### `/stats` (solo admins)
Muestra estadísticas de uso del bot.

**Muestra:**
- Usuarios únicos
- Total de comandos ejecutados
- Comandos más usados
- Últimos 10 comandos
- Tiempo activo del bot

---

## Diferencias entre comandos

### `/aprs` vs `/info`

| Característica | `/aprs` | `/info` |
|----------------|---------|---------|
| Fuente de datos | aprs.fi API | TrackDirect BD |
| Información | Básica | Completa |
| Estadísticas | ❌ No | ✅ Sí |
| Histórico | ❌ No | ✅ Sí (stats) |
| Formato | Texto simple | Rico con emojis |
| Movimiento | ❌ No | ✅ Velocidad/rumbo |

**Recomendación:** Usar `/info` para información completa y actualizada.

### `/telemetria` antiguo vs nuevo

| Característica | Antiguo (aprs.fi) | Nuevo (TrackDirect) |
|----------------|-------------------|---------------------|
| Fuente | aprs.fi API | TrackDirect BD |
| Histórico | ❌ No | ✅ 24 horas |
| Tendencias | ❌ No | ✅ Sí |
| Formato | Básico | Rico con barras y emojis |
| Interpretación | Números crudos | Labels descriptivos |
| Bits digitales | Array de números | Estados legibles |

---

## Emojis usados

- 📡 Estación APRS
- 📍 Posición/ubicación
- 🚗 Móvil en movimiento
- 🏠 Estación fija
- 🌡️ Estación meteorológica
- 📊 Estadísticas/telemetría
- 🔋 Batería/alimentación
- ☀️ Panel solar
- 📈 Tendencia/gráfico
- ✅ Estado activo/OK
- ❌ Estado inactivo/fallo
- ⚡ Alimentación normal
- 🔌 Low power mode
- 📶 Señal buena
- 📡 Señal media
- 📊 Señal débil

---

### `/track <indicativo>` ⭐ NUEVO
Muestra tracking de últimas posiciones con ruta detallada.

**Ejemplo:** `/track LU1QA-1`

**Muestra:**
- Últimas 10-20 posiciones con timestamps
- Velocidad y rumbo en cada punto
- Distancia total recorrida
- Tiempo en movimiento
- Velocidad promedio

**Formato de salida:**
```
🚗 Track de LU1QA-1

📍 Últimas 10 posiciones

🕐 17:45 → (-34.6037°, -58.3816°)
   🧭 45° NE | 65 km/h 🚗 | 🏔️ 25m

🕐 17:40 → (-34.6245°, -58.4012°)
   🧭 42° NE | 70 km/h 🚗 | 🏔️ 30m

...

📊 Resumen
├─ 📏 Distancia: 45.2 km
├─ ⏱️ Duración: 1h 25m
└─ 🏁 Velocidad promedio: 68 km/h
```

---

### `/cerca <indicativo> [radio]` ⭐ NUEVO
Lista estaciones cercanas a una estación dada.

**Ejemplo:**
- `/cerca LU1QA-1` (radio por defecto: 50 km)
- `/cerca LU1QA-1 100` (radio: 100 km)

**Parámetros:**
- `indicativo`: Estación de referencia
- `radio`: Radio de búsqueda en km (1-500, opcional)

**Muestra:**
- Lista de hasta 15 estaciones cercanas
- Distancia y dirección a cada una
- Tipo de estación (móvil, fija, WX, etc.)
- Última actividad

**Formato de salida:**
```
📍 Estaciones cerca de LU1QA-1
Radio de búsqueda: 50 km

1. LU2ABC-5 🏠
   📏 12.5 km al Noreste
   🕐 hace 10 minutos

2. LU3XYZ-9 🌡️
   📏 28.3 km al Sur
   🕐 hace 2 minutos

3. LU4DEF 📡
   📏 45.1 km al Oeste
   🕐 hace 1 minuto

Total: 8 estaciones activas
```

---

### `/clima <indicativo>` ⭐ NUEVO
Datos meteorológicos completos con tendencias.

**Ejemplo:** `/clima LU1QA-13`

**Muestra:**
- 🌡️ Temperatura (actual, min/max del día)
- 💧 Humedad con indicador
- 🌬️ Viento (velocidad, ráfagas, dirección)
- ☔ Lluvia (última hora, últimas 24h)
- 📊 Presión atmosférica con tendencia
- 🕐 Última actualización

**Formato de salida:**
```
🌦️ Estación WX: LU1QA-13

🌡️ Temperatura
└─ 22.5°C ☀️

   Min/Max hoy: 18.0°C / 25.0°C

💧 Humedad
└─ 65% ⛅

🌬️ Viento
├─ Velocidad: 15 km/h desde 270° O
└─ Ráfagas: 25 km/h

☔ Lluvia
├─ Última hora: 0.0 mm
└─ Últimas 24h: 2.5 mm

📊 Presión atmosférica
└─ 1013.2 hPa → (estable)

🕐 Última actualización
└─ hace 3 minutos
```

**Características:**
- ✅ Datos en tiempo real desde TrackDirect
- 📊 Histórico para calcular min/max
- 📈 Tendencias de presión
- 🌡️ Emojis descriptivos según condiciones

---

### `/ssid <indicativo>` - MEJORADO
Lista todos los SSID activos de un indicativo base.

**Ejemplo:** `/ssid LU1QA`

**Formato mejorado:**
```
📡 SSID activos para LU1QA

• LU1QA-10
• LU1QA-8
• LU1QA-1
• LU1QA-7
• LU1QA-2
• LU1QA-9
• LU1QA
• LU1QA-15

Total: 8 SSIDs encontrados

💡 Usa /aprs LU1QA-10 para ver última posición de un SSID específico
```

---

## Próximos comandos (en desarrollo)

### `/path <indicativo>` - Ruta de paquetes
- Camino que siguió el último paquete
- Digipeaters e IGates usados
- Calidad y delays

---

## Notas técnicas

### Conexión a TrackDirect
El bot se conecta automáticamente a la base de datos de TrackDirect al iniciarse. Los comandos `/info` y `/telemetria` obtienen datos directamente de PostgreSQL.

### Pool de conexiones
Se utiliza asyncpg con un pool de 2-10 conexiones para manejar múltiples consultas simultáneas eficientemente.

### Zona horaria
Todos los timestamps se muestran en hora de Argentina (GMT-3 / ART).
