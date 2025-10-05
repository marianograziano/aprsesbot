# 🛠️ Scripts de TrackDirect

## generate-config.sh

Script para generar automáticamente los archivos de configuración de TrackDirect desde las variables de entorno.

### Uso

```bash
./scripts/generate-config.sh
```

### Prerequisitos

1. Tener el archivo `.env` configurado:
```bash
cp .env.example .env
nano .env
```

2. Variables requeridas:
- `APRS_CALLSIGN`: Tu indicativo APRS
- `APRS_PASSCODE`: Tu passcode APRS

### Archivos generados

El script genera automáticamente:

1. **config/trackdirect.ini**
   - Configuración principal de TrackDirect
   - Incluye filtro geográfico si está definido en `APRS_FILTER`
   - Configura websocket y collector

2. **config/aprsc.conf**
   - Configuración del servidor APRS interno
   - Usa variables de `APRSC_*` en .env

3. **config/postgresql.conf**
   - Configuración de PostgreSQL
   - Optimizada para rendimiento

### Ejemplo de salida

```
=== Generando archivos de configuración de TrackDirect ===

Generando config/trackdirect.ini...
✓ config/trackdirect.ini generado

Generando config/aprsc.conf...
✓ config/aprsc.conf generado

Generando config/postgresql.conf...
✓ config/postgresql.conf generado

=== Configuración generada exitosamente ===

Filtro geográfico configurado: a/-21/-73/-55/-53

Siguiente paso:
  docker-compose up -d
```

### Regenerar configuración

Si cambias valores en `.env`, simplemente vuelve a ejecutar el script:

```bash
# Editar .env
nano .env

# Regenerar configuración
./scripts/generate-config.sh

# Reiniciar servicios
docker-compose restart
```

### Variables de entorno soportadas

#### TrackDirect
- `APRS_CALLSIGN`: Indicativo APRS
- `APRS_PASSCODE`: Passcode APRS
- `APRS_FILTER`: Filtro geográfico (ej: `a/-21/-73/-55/-53`)

#### Sitio web
- `SITE_TITLE`: Título del sitio
- `SITE_OWNER_NAME`: Nombre del propietario
- `SITE_OWNER_URL`: URL del propietario

#### API Keys (opcional)
- `MAPTILER_KEY`: API key de MapTiler
- `GOOGLE_MAPS_KEY`: API key de Google Maps
- `HERE_MAPS_KEY`: API key de HERE Maps

#### Base de datos
- `POSTGRES_USER`: Usuario PostgreSQL
- `POSTGRES_PASSWORD`: Contraseña PostgreSQL
- `POSTGRES_DB`: Nombre de la base de datos
- `POSTGRES_SHARED_BUFFERS`: Memoria compartida (default: 2048MB)
- `POSTGRES_CACHE_SIZE`: Tamaño de caché (default: 6GB)

#### Servidor APRS
- `APRSC_SERVER_ID`: ID del servidor
- `APRSC_SERVER_PASS`: Password del servidor
- `APRSC_ADMIN_INFO`: Información del admin
- `APRSC_EMAIL`: Email de contacto
