# 🛠️ Instalación de TrackDirect

## Requisitos previos

- Docker y Docker Compose instalados
- Git
- 4GB+ RAM
- Espacio en disco para la base de datos

## Pasos de instalación

### 1. Clonar el repositorio de TrackDirect

Desde el directorio del proyecto (`aprs-telegram-bot/`):

```bash
git clone https://github.com/qvarforth/trackdirect.git
```

Esto creará un directorio `trackdirect/` con todos los Dockerfiles necesarios.

### 2. Configurar variables de entorno

```bash
cp .env.example .env
nano .env
```

**Variables importantes a configurar:**

```bash
# Bot de Telegram
APRS_API_KEY="tu_api_key_de_aprs_fi"
TELEGRAM_TOKEN="tu_token_de_telegram"
ADMIN_USER_ID="123456789"

# TrackDirect - APRS
APRS_CALLSIGN="TU_INDICATIVO"  # Ejemplo: LU1QA-1
APRS_PASSCODE="tu_passcode"    # Generar en https://apps.magicbug.co.uk/passcode/

# Filtro geográfico para Argentina (ya configurado)
APRS_FILTER="a/-21/-73/-55/-53"

# Información del sitio
SITE_TITLE="APRS Track Direct Argentina"
SITE_OWNER_NAME="Tu Nombre"
APRSC_ADMIN_INFO="Tu Nombre, TU_INDICATIVO"
APRSC_EMAIL="tu_email@example.com"
```

**⚠️ IMPORTANTE:** Los valores con espacios deben estar entre comillas:
```bash
✅ CORRECTO:   APRSC_ADMIN_INFO="Mariano, LU8QCG"
❌ INCORRECTO: APRSC_ADMIN_INFO=Mariano, LU8QCG
```

### 3. Generar archivos de configuración

```bash
./scripts/generate-config.sh
```

Este script genera automáticamente:
- `config/trackdirect.ini`
- `config/aprsc.conf`
- `config/postgresql.conf`

### 4. Verificar estructura de directorios

Tu estructura debería verse así:

```
aprs-telegram-bot/
├── trackdirect/          # ← Clonado de GitHub
├── config/
│   ├── aprsc.conf        # ← Generado por script
│   ├── trackdirect.ini   # ← Generado por script
│   └── postgresql.conf   # ← Generado por script
├── .env                  # ← Configurado por ti
├── docker-compose.yml
└── ...
```

### 5. Construir y levantar los servicios

**Primera vez (construye las imágenes):**
```bash
docker-compose up -d --build
```

Esto tomará varios minutos la primera vez mientras construye todas las imágenes.

**Verificar que están corriendo:**
```bash
docker-compose ps
```

Deberías ver:
```
trackdirect-aprsc      running
trackdirect-collector  running
trackdirect-websocket  running
trackdirect-cron       running
trackdirect-web        running (0.0.0.0:80->80/tcp)
trackdirect-db         running
aprs-bot               running
```

### 6. Ver logs

```bash
# Todos los servicios
docker-compose logs -f

# Solo un servicio específico
docker-compose logs -f collector
docker-compose logs -f aprs-bot
```

### 7. Acceder a TrackDirect

Una vez que todo esté corriendo:
- Web: http://tu-servidor (puerto 80)
- Bot de Telegram: Busca tu bot y usa `/start`

## Solución de problemas

### Error: "command not found" al ejecutar generate-config.sh

**Causa:** Valores con espacios sin comillas en `.env`

**Solución:** Agregar comillas a todos los valores:
```bash
SITE_TITLE="APRS Track Direct Argentina"
APRSC_ADMIN_INFO="Mariano, LU8QCG"
```

### Error: "pull access denied for qvarforth/trackdirect-*"

**Causa:** Falta clonar el repositorio de TrackDirect

**Solución:**
```bash
git clone https://github.com/qvarforth/trackdirect.git
docker-compose up -d --build
```

### Error: "no se puede conectar a PostgreSQL"

**Causa:** La base de datos aún no está lista

**Solución:** Esperar 30-60 segundos y reintentar:
```bash
docker-compose restart collector websocket aprs-bot
```

### No aparecen datos en TrackDirect

**Posibles causas:**

1. **Filtro geográfico muy restrictivo:** Verifica que haya actividad APRS en tu área
2. **Credenciales APRS incorrectas:** Verifica APRS_CALLSIGN y APRS_PASSCODE
3. **Collector no está corriendo:** `docker-compose logs -f collector`

**Verificar recolección de datos:**
```bash
# Ver si collector está recibiendo paquetes
docker-compose logs -f collector | grep -i "insert\|packet"

# Ver estaciones en la BD
docker-compose exec db psql -U postgres -d trackdirect -c "SELECT COUNT(*) FROM station;"
```

### Bot no se conecta a TrackDirect

**Verificar conexión:**
```bash
# Ver logs del bot
docker-compose logs -f aprs-bot

# Debería ver:
# "Inicializando pool de conexiones a TrackDirect..."
# "Pool de conexiones inicializado"
```

**Si falla la conexión:**
- Verificar que `POSTGRES_HOST=db` (nombre del servicio)
- Verificar que la red `aprs-network` existe
- Reiniciar el bot: `docker-compose restart aprs-bot`

## Comandos útiles

```bash
# Detener todos los servicios
docker-compose down

# Detener y eliminar volúmenes (⚠️ borra la BD)
docker-compose down -v

# Reconstruir solo el bot
docker-compose up -d --build aprs-bot

# Ver uso de recursos
docker stats

# Acceder a la BD directamente
docker-compose exec db psql -U postgres -d trackdirect

# Backup de la BD
docker-compose exec db pg_dump -U postgres trackdirect > backup.sql
```

## Actualizar TrackDirect

```bash
cd trackdirect/
git pull
cd ..
docker-compose up -d --build
```

## Desinstalación

```bash
# Detener servicios y eliminar todo
docker-compose down -v

# Eliminar directorio de TrackDirect
rm -rf trackdirect/

# Limpiar imágenes huérfanas
docker system prune -a
```
