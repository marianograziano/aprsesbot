#!/bin/bash
# Script para generar archivos de configuración desde .env

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Generando archivos de configuración de TrackDirect ===${NC}\n"

# Verificar que existe .env
if [ ! -f .env ]; then
    echo -e "${RED}Error: No existe el archivo .env${NC}"
    echo -e "${YELLOW}Ejecuta: cp .env.example .env${NC}"
    echo -e "${YELLOW}Luego edita .env con tus valores${NC}"
    exit 1
fi

# Cargar variables de .env
source .env

# Verificar variables requeridas
if [ -z "$APRS_CALLSIGN" ] || [ "$APRS_CALLSIGN" = "N0CALL" ]; then
    echo -e "${YELLOW}Advertencia: APRS_CALLSIGN no está configurado correctamente${NC}"
fi

if [ -z "$APRS_PASSCODE" ] || [ "$APRS_PASSCODE" = "-1" ]; then
    echo -e "${YELLOW}Advertencia: APRS_PASSCODE no está configurado${NC}"
    echo -e "${YELLOW}Genera tu passcode en: https://apps.magicbug.co.uk/passcode/${NC}"
fi

# Crear directorio config si no existe
mkdir -p config

echo -e "${GREEN}Generando config/trackdirect.ini...${NC}"

# Generar trackdirect.ini
cat > config/trackdirect.ini << EOF
# TrackDirect Configuration
# Generado automáticamente desde .env

[website]
title = ${SITE_TITLE:-APRS Track Direct}
owner_name = ${SITE_OWNER_NAME:-}
owner_url = ${SITE_OWNER_URL:-}

# API Keys de mapas (opcional)
EOF

# Agregar API keys solo si están definidas
if [ ! -z "$MAPTILER_KEY" ]; then
    echo "maptiler_key = ${MAPTILER_KEY}" >> config/trackdirect.ini
fi
if [ ! -z "$GOOGLE_MAPS_KEY" ]; then
    echo "google_key = ${GOOGLE_MAPS_KEY}" >> config/trackdirect.ini
fi
if [ ! -z "$HERE_MAPS_KEY" ]; then
    echo "here_key = ${HERE_MAPS_KEY}" >> config/trackdirect.ini
fi

# Continuar con el resto de trackdirect.ini
cat >> config/trackdirect.ini << EOF

# Proveedor de tiles Leaflet
leaflet_tile_provider_name = OpenStreetMap
leaflet_tile_provider_url = https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png
leaflet_tile_provider_attribution = &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors

# Configuración de cobertura
coverage_send_data_limit = 20
coverage_enable_igates = 1
coverage_enable_digipeaters = 1

[database]
host = db
username = ${POSTGRES_USER:-postgres}
password = ${POSTGRES_PASSWORD:-trackdirect}
database = ${POSTGRES_DB:-trackdirect}
port = 5432

# Retención de datos (días)
data_retention_days = 365
telemetry_retention_days = 90
weather_retention_days = 30
position_retention_days = 30

handle_ogn_missing_identity = 1

[websocket]
host = 0.0.0.0
port = 9000
log_level = ERROR

# Servidor APRS
aprs_server_host = aprsc
aprs_server_port = 10152
aprs_server_callsign = ${APRS_CALLSIGN:-N0CALL}
aprs_server_passcode = ${APRS_PASSCODE:--1}
EOF

# Agregar filtro si está definido
if [ ! -z "$APRS_FILTER" ]; then
    echo "aprs_server_filter = ${APRS_FILTER}" >> config/trackdirect.ini
fi

cat >> config/trackdirect.ini << EOF

# Límites
packet_frequency_limit = 60
enable_time_travel = 1
client_idle_time_limit = 3600

[collector]
aprs_server_host = aprsc
aprs_server_port = 10152
aprs_server_callsign = ${APRS_CALLSIGN:-N0CALL}
aprs_server_passcode = ${APRS_PASSCODE:--1}
EOF

# Agregar filtro al collector si está definido
if [ ! -z "$APRS_FILTER" ]; then
    echo "aprs_server_filter = ${APRS_FILTER}" >> config/trackdirect.ini
fi

cat >> config/trackdirect.ini << EOF

# Procesamiento de paquetes
duplicate_detection_time = 300
packet_frequency_limit = 60
batch_insert_size = 1000
EOF

echo -e "${GREEN}✓ config/trackdirect.ini generado${NC}"

# Generar aprsc.conf
echo -e "${GREEN}Generando config/aprsc.conf...${NC}"

cat > config/aprsc.conf << EOF
# APRS Server Configuration
# Generado automáticamente desde .env

ServerId ${APRSC_SERVER_ID:-APRS-SERVER}
ServerPass ${APRSC_SERVER_PASS:-12345}
MyAdmin "${APRSC_ADMIN_INFO:-}"
MyEmail ${APRSC_EMAIL:-}

# Puertos de escucha
Listen fullfeed tcp 10152 fullfeed
Listen clientfiltered tcp 14580 filter
Listen dupefeed tcp 10155 dupefeed

# Conexión a servidor APRS upstream
Uplink "rotate.aprs.net" 10152

# Página de estado HTTP
HTTPStatus 14501

# Configuración de logs
LogRotate "megabytes 10"

# Timeout de conexión
ClientTimeout 30
EOF

echo -e "${GREEN}✓ config/aprsc.conf generado${NC}"

# Generar postgresql.conf
echo -e "${GREEN}Generando config/postgresql.conf...${NC}"

cat > config/postgresql.conf << EOF
# PostgreSQL Configuration
# Generado automáticamente

# Memoria
shared_buffers = ${POSTGRES_SHARED_BUFFERS:-2048MB}
effective_cache_size = ${POSTGRES_CACHE_SIZE:-6GB}
work_mem = 64MB
maintenance_work_mem = 512MB

# Escritura y commit
synchronous_commit = off
commit_delay = 100000
wal_buffers = 16MB
checkpoint_completion_target = 0.9

# Logs
log_destination = 'stderr'
logging_collector = on
log_directory = '/var/log/postgresql'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_rotation_age = 1d
log_rotation_size = 100MB

# Rendimiento
max_connections = 100
EOF

echo -e "${GREEN}✓ config/postgresql.conf generado${NC}"

echo ""
echo -e "${GREEN}=== Configuración generada exitosamente ===${NC}"
echo ""

# Mostrar filtro configurado
if [ ! -z "$APRS_FILTER" ]; then
    echo -e "${GREEN}Filtro geográfico configurado:${NC} ${APRS_FILTER}"
    echo ""
fi

# Mostrar advertencias si es necesario
if [ "$APRS_CALLSIGN" = "N0CALL" ] || [ "$APRS_PASSCODE" = "-1" ]; then
    echo -e "${YELLOW}⚠ IMPORTANTE: Debes configurar tu indicativo y passcode APRS en .env${NC}"
    echo -e "${YELLOW}   Edita .env y ejecuta nuevamente este script${NC}"
    echo ""
fi

echo -e "${GREEN}Siguiente paso:${NC}"
echo -e "  docker-compose up -d"
echo ""
