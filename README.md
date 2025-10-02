# 📡 APRS Telegram Bot

Bot de Telegram en español para consultar datos APRS (Automatic Packet Reporting System).

## ✨ Características

- 🌍 Consulta posiciones APRS en tiempo real
- 🌦️ Datos meteorológicos de estaciones WX
- 📋 Lista de SSID activos para indicativos
- 📊 Telemetría de estaciones
- 👥 Soporte para múltiples administradores
- 🕐 Zona horaria Argentina (GMT-3)

## 🚀 Comandos disponibles

- `/aprs <indicativo>` - Última posición APRS
- `/wx <indicativo>` - Datos meteorológicos
- `/ssid <indicativo>` - Lista de SSID usados
- `/stats` - Estadísticas del bot (solo admins)

## 📋 Requisitos

- Python 3.8+
- Docker y Docker Compose
- API Key de [aprs.fi](https://aprs.fi/)
- Bot Token de Telegram

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
# Edita .env con tus credenciales
```

3. Ejecuta con Docker:
```bash
docker-compose up -d
```

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

- `APRS_API_KEY`: Tu API key de aprs.fi
- `TELEGRAM_TOKEN`: Token de tu bot de Telegram
- `ADMIN_USER_ID`: IDs de usuarios admin (separados por comas)


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
├── bot.py              # Bot principal
├── web_dashboard.py    # Dashboard web
├── requirements.txt    # Dependencias Python
├── Dockerfile         # Imagen Docker
├── docker-compose.yml # Configuración Docker
├── .env.example       # Ejemplo de configuración
├── templates/
│   └── logs.html      # Template del dashboard
└── docs/
    └── api.md         # Documentación de la API
```

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

Basado en @APRSBOT original. Desarrollado para la comunidad radioaficionada argentina.
