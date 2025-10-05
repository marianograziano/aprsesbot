# 🌍 Filtros Geográficos APRS

## ¿Qué son los filtros geográficos?

Los filtros geográficos permiten limitar los datos APRS que TrackDirect captura y almacena, enfocándose en una región específica. Esto reduce el uso de ancho de banda, almacenamiento y procesamiento.

## Tipos de filtros disponibles

### 1. Area Filter (Filtro de área rectangular)

Filtra paquetes dentro de un área rectangular definida por coordenadas.

**Sintaxis:** `a/latN/lonW/latS/lonE`

- `latN`: Latitud Norte (límite superior)
- `lonW`: Longitud Oeste (límite izquierdo)
- `latS`: Latitud Sur (límite inferior)
- `lonE`: Longitud Este (límite derecho)

**Ejemplo para Argentina:**
```bash
APRS_FILTER=a/-21/-73/-55/-53
```

Coordenadas de Argentina:
- Norte: -21° (frontera con Bolivia/Paraguay)
- Oeste: -73° (frontera con Chile)
- Sur: -55° (Tierra del Fuego)
- Este: -53° (costa atlántica)

### 2. Range Filter (Filtro de radio)

Filtra paquetes dentro de un radio desde un punto central.

**Sintaxis:** `r/lat/lon/dist`

- `lat`: Latitud del centro
- `lon`: Longitud del centro
- `dist`: Radio en kilómetros

**Ejemplo para Argentina:**
```bash
APRS_FILTER=r/-34/-64/2500
```

- Centro aproximado de Argentina: -34° lat, -64° lon
- Radio: 2500 km (cubre todo el país)

### 3. Filtros múltiples

Puedes combinar múltiples filtros para áreas complejas.

**Ejemplo Argentina + países vecinos:**
```bash
APRS_FILTER=a/-21/-73/-55/-53 a/-17/-69/-23/-57
```

## Regiones de Argentina

### Buenos Aires y CABA
```bash
APRS_FILTER=r/-34.6/-58.4/300
```

### Patagonia
```bash
APRS_FILTER=a/-39/-73/-55/-63
```

### NOA (Noroeste Argentino)
```bash
APRS_FILTER=a/-22/-68/-29/-62
```

### Córdoba y región central
```bash
APRS_FILTER=r/-31.4/-64.2/400
```

### Cuyo (Mendoza, San Juan, San Luis)
```bash
APRS_FILTER=a/-28/-70/-35/-65
```

## Configuración en TrackDirect

### Opción 1: Usando el script automático

1. Edita el archivo `.env`:
```bash
APRS_FILTER=a/-21/-73/-55/-53
```

2. Ejecuta el script de generación:
```bash
./scripts/generate-config.sh
```

### Opción 2: Configuración manual

Edita `config/trackdirect.ini` y agrega en las secciones `[websocket]` y `[collector]`:

```ini
[websocket]
aprs_server_filter = a/-21/-73/-55/-53

[collector]
aprs_server_filter = a/-21/-73/-55/-53
```

## Otros tipos de filtros

### Friend Range Filter
Sigue a un indicativo específico:
```bash
f/LU1ABC/500
```

### Prefix Filter
Filtra por prefijo de indicativo:
```bash
p/LU/LW
```

### Combinar filtros
```bash
a/-21/-73/-55/-53 p/LU/LW
```

## Verificar que el filtro funciona

1. Inicia los servicios:
```bash
docker-compose up -d
```

2. Verifica los logs del collector:
```bash
docker-compose logs -f collector
```

3. Deberías ver solo paquetes de la región configurada.

## Performance

### Sin filtro (mundial)
- ~500-2000 paquetes/minuto
- Base de datos crece rápidamente
- Requiere más RAM y CPU

### Con filtro (Argentina)
- ~20-100 paquetes/minuto (depende de actividad)
- Base de datos más manejable
- Menor uso de recursos

## Recursos adicionales

- [APRS-IS Filter Guide](http://www.aprs-is.net/javAPRSFilter.aspx)
- [APRS Coverage Argentina](https://aprs.fi/#!lat=-34&lng=-64&z=5)
- [Calculadora de coordenadas](https://www.latlong.net/)
