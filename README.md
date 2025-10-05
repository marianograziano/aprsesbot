# 📡 APRS Telegram Bot + TrackDirect

Bot de Telegram en español para consultar datos APRS (Automatic Packet Reporting System) integrado con TrackDirect, un sistema completo de tracking APRS en tiempo real.

## ✨ Características

### Bot de Telegram
- 🌍 Consulta posiciones APRS en tiempo real
- 🌦️ Datos meteorológicos de estaciones WX
- 📋 Lista de SSID activos para indicativos
- 📊 Telemetría de estaciones
- 👥 Soporte para múltiples administradores
- 🕐 Zona horaria Argentina (GMT-3)

### TrackDirect
- 🗺️ Interfaz web con mapas interactivos (Leaflet/Google Maps)
- 📡 Recolección de datos APRS en tiempo real desde APRS-IS
- 🔄 WebSocket para actualizaciones en vivo
- 💾 Almacenamiento persistente en PostgreSQL
- 📈 Visualización de rutas y estadísticas
- 🌐 Sitio web completo de tracking APRS

## 🚀 Comandos disponibles

- `/aprs <indicativo>` - Última posición APRS
- `/wx <indicativo>` - Datos meteorológicos
- `/ssid <indicativo>` - Lista de SSID usados
- `/stats` - Estadísticas del bot (solo admins)

## 📋 Requisitos

- Python 3.8+
- Docker y Docker Compose
- API Key de [aprs.fi](https://aprs.fi/) (para el bot)
- Bot Token de Telegram
- 4GB+ RAM (recomendado para TrackDirect)

## ⚙️ Instalación

### Opción 1: Docker (Recomendado)

1. Clona el repositorio:
```bash
git clone https://github.com/marianograziano/aprs-telegram-bot.git
cd aprs-telegram-bot
```

2. Configura las variables de entorno:
```bash
cp .env.example .env
nano .env  # Edita con tus credenciales
```

**Variables importantes a configurar:**
- `APRS_API_KEY`: Tu API key de aprs.fi
- `TELEGRAM_TOKEN`: Token de tu bot
- `ADMIN_USER_ID`: Tu ID de Telegram
- `APRS_CALLSIGN`: Tu indicativo APRS (ej: LU1ABC-1)
- `APRS_PASSCODE`: Tu passcode APRS ([generar aquí](https://apps.magicbug.co.uk/passcode/))
- `APRS_FILTER`: Filtro geográfico para Argentina (ya configurado)

3. Genera los archivos de configuración automáticamente:
```bash
./scripts/generate-config.sh
```

Este script genera automáticamente:
- `config/trackdirect.ini` - Configuración principal
- `config/aprsc.conf` - Servidor APRS
- `config/postgresql.conf` - Base de datos

**Filtro geográfico incluido:** Por defecto captura solo datos de Argentina. Ver [docs/filtros-geograficos.md](docs/filtros-geograficos.md) para otras opciones.

4. Ejecuta con Docker:
```bash
docker-compose up -d
```

5. Accede a TrackDirect:
- Sitio web: http://localhost
- El bot de Telegram estará activo automáticamente

### Opción 2: Instalación manual

1. Instala dependencias:
```bash
pip install -r requirements.txt
```

2. Configura variables de entorno:
```bash
export APRS_API_KEY="tu_api_key"
export TELEGRAM_TOKEN="tu_bot_token"
export ADMIN_USER_ID="tu_telegram_id"
```

3. Ejecuta el bot:
```bash
python bot.py
```

## 🔧 Configuración

### Variables de entorno requeridas:

#### Bot de Telegram
- `APRS_API_KEY`: Tu API key de aprs.fi
- `TELEGRAM_TOKEN`: Token de tu bot de Telegram
- `ADMIN_USER_ID`: IDs de usuarios admin (separados por comas)

#### TrackDirect (opcional)
- `POSTGRES_USER`: Usuario de PostgreSQL (default: postgres)
- `POSTGRES_PASSWORD`: Contraseña de PostgreSQL (default: trackdirect)
- `POSTGRES_DB`: Nombre de la base de datos (default: trackdirect)

### Configuración de TrackDirect

Los archivos de configuración están en el directorio `config/`:

#### `trackdirect.ini`
- **[website]**: Título del sitio, información del propietario, API keys de mapas
- **[database]**: Conexión a PostgreSQL, retención de datos
- **[websocket]**: Configuración del servidor WebSocket en tiempo real
- **[collector]**: Recolector de datos APRS, callsign y passcode

#### `aprsc.conf`
- Configuración del servidor APRS interno
- Debes actualizar: `ServerId`, `ServerPass`, `MyAdmin`, `MyEmail`
- Los puertos 10152 (fullfeed) y 14580 (filtered) se usan internamente

#### `postgresql.conf`
- Configuración optimizada para rendimiento
- `shared_buffers`: Ajustar según RAM disponible (25% recomendado)
- `effective_cache_size`: 50-75% de RAM total

### Generación de passcode APRS

Para generar tu passcode APRS:
```bash
# Visita: https://apps.magicbug.co.uk/passcode/
# O usa Python:
python -c "from hashlib import md5; callsign='TU_INDICATIVO'; print(int(md5(callsign.upper().encode()).hexdigest()[:4], 16) & 0x7fff)"
```

### Filtros geográficos

Por defecto, TrackDirect está configurado para capturar **solo datos de Argentina** usando un filtro de área:

```bash
APRS_FILTER=a/-21/-73/-55/-53  # Bounding box de Argentina
```

**Opciones de filtro:**

1. **Todo Argentina** (recomendado):
   ```bash
   APRS_FILTER=a/-21/-73/-55/-53
   ```

2. **Radio desde centro de Argentina** (alternativa):
   ```bash
   APRS_FILTER=r/-34/-64/2500
   ```

3. **Solo Buenos Aires y alrededores**:
   ```bash
   APRS_FILTER=r/-34.6/-58.4/300
   ```

4. **Sin filtro** (todo el mundo - ⚠️ alto consumo de recursos):
   ```bash
   # APRS_FILTER=
   ```

Ver documentación completa en [docs/filtros-geograficos.md](docs/filtros-geograficos.md)

## 📊 Funcionalidades adicionales

### Estadísticas
- Tracking de usuarios únicos
- Comandos más utilizados
- Logs detallados con timestamps
- Información de administradores

### Múltiples administradores
```bash
# En .env
ADMIN_USER_ID=123456789,987654321,456123789
```

## 🛠️ Desarrollo

### Estructura del proyecto
```
aprs-telegram-bot/
├── bot.py                    # Bot principal de Telegram
├── stats_web.py              # Dashboard web de estadísticas
├── requirements.txt          # Dependencias Python
├── Dockerfile                # Imagen Docker del bot
├── docker-compose.yml        # Configuración completa (bot + TrackDirect)
├── .env.example              # Ejemplo de configuración
├── config/                   # Configuración de TrackDirect
│   ├── trackdirect.ini       # Config principal de TrackDirect
│   ├── aprsc.conf            # Config del servidor APRS
│   └── postgresql.conf       # Config de PostgreSQL
└── htdocs/                   # Contenido web de TrackDirect (auto-generado)
    └── public/
```

### Servicios Docker

El proyecto incluye los siguientes servicios:
- **aprs-bot**: Bot de Telegram
- **aprsc**: Servidor APRS (recibe datos de APRS-IS)
- **collector**: Recolector de datos APRS
- **websocket**: Servidor WebSocket para actualizaciones en tiempo real
- **cron**: Tareas programadas
- **web**: Servidor web Apache (interfaz TrackDirect)
- **db**: Base de datos PostgreSQL

## 📄 Licencia

MIT License - Ver archivo LICENSE para más detalles.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una branch para tu feature
3. Commit tus cambios
4. Push a la branch
5. Abre un Pull Request

## 📞 Soporte

- Issues: [GitHub Issues](https://github.com/marianograziano/aprs-telegram-bot/issues)
- Contacto: mariano.graziano@gmail.com

## 🙏 Créditos

- Bot de Telegram basado en @APRSBOT original
- TrackDirect por [qvarforth](https://github.com/qvarforth/trackdirect)
- Desarrollado para la comunidad radioaficionada argentina

### Enlaces útiles
- [TrackDirect GitHub](https://github.com/qvarforth/trackdirect)
- [APRS.fi](https://aprs.fi/)
- [APRS-IS Documentation](http://www.aprs-is.net/)
