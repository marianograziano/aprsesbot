import os
import requests
import logging
from datetime import datetime, timezone, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Módulos de TrackDirect
import trackdirect_db as tdb
import telegram_formatters as fmt

# Configuración de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Zona horaria GMT-3 (Argentina)
ARGENTINA_TZ = timezone(timedelta(hours=-3))

# Variables de entorno
APRS_API_KEY = os.getenv("APRS_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_USER_ID = os.getenv("ADMIN_USER_ID")

# 🔧 NUEVO: Función para manejar múltiples admins
def get_admin_users():
    """Obtiene la lista de usuarios admin desde variable de entorno"""
    if not ADMIN_USER_ID:
        return []
    
    # Permitir múltiples IDs separados por comas
    admin_ids = [id.strip() for id in ADMIN_USER_ID.split(',')]
    return admin_ids

def is_admin(user_id):
    """Verifica si un usuario es admin"""
    admin_users = get_admin_users()
    return str(user_id) in admin_users

# Estadísticas de uso
usage_stats = {
    "total_users": set(),
    "commands_used": [],
    "start_time": datetime.now(ARGENTINA_TZ)
}

def get_user_display_name(user):
    """Obtiene el mejor nombre para mostrar del usuario"""
    if user.username:
        return f"@{user.username}"
    elif user.first_name:
        full_name = user.first_name
        if user.last_name:
            full_name += f" {user.last_name}"
        return full_name
    else:
        return f"ID:{user.id}"

def log_command(user, command):
    """Registra un comando en las estadísticas"""
    usage_stats["total_users"].add(user.id)
    usage_stats["commands_used"].append({
        "user_id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "command": command,
        "timestamp": datetime.now(ARGENTINA_TZ).isoformat()
    })

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    log_command(user, "/start")
    logger.info(f"Usuario {get_user_display_name(user)} ({user.id}) usó /start")
    
    # 🔧 MEJORADO: Mostrar si es admin
    admin_text = " (ADMIN)" if is_admin(user.id) else ""
    
    await update.message.reply_text(
        f"Bienvenido al Bot APRS en Español + TrackDirect.\n\n"
        f"Tu ID de Telegram es: `{user.id}`\n"
        f"Usuario: {get_user_display_name(user)}{admin_text}\n\n"
        "📡 *Comandos principales:*\n"
        "/info <indicativo> → Info completa ⭐\n"
        "/track <indicativo> → Tracking de ruta ⭐\n"
        "/cerca <indicativo> [radio] → Estaciones cercanas ⭐\n"
        "/clima <indicativo> → Meteorología completa ⭐\n"
        "/telemetria <indicativo> → Telemetría con tendencias ⭐\n\n"
        "📋 *Comandos básicos:*\n"
        "/aprs <indicativo> → Última posición\n"
        "/wx <indicativo> → Datos meteorológicos\n"
        "/ssid <indicativo> → Lista de SSID\n"
        "/help → Ayuda completa\n"
        f"{'/stats → Estadísticas del bot (solo admin)' if is_admin(user.id) else ''}",
        parse_mode='Markdown'
    )

# /aprs
async def aprs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not context.args:
        logger.warning(f"Usuario {get_user_display_name(user)} ({user.id}) usó /aprs sin argumentos")
        await update.message.reply_text("Debes escribir un indicativo. Ejemplo: /aprs LU1QA-1")
        return

    call = context.args[0]
    log_command(user, f"/aprs {call}")
    logger.info(f"Usuario {get_user_display_name(user)} ({user.id}) consultó APRS para {call}")
    
    url = f"https://api.aprs.fi/api/get?name={call}&what=loc&apikey={APRS_API_KEY}&format=json"
    r = requests.get(url).json()
    
    if r.get("entries"):
        entry = r["entries"][0]
        msg = (f"Última posición de {call}:\n"
               f"Lat: {entry['lat']} | Lon: {entry['lng']}\n"
               f"Hora: {entry['time']}\n"
               f"Comentario: {entry.get('comment','-')}")
    else:
        msg = f"No encontré datos APRS para {call}."
    
    await update.message.reply_text(msg)

# /wx
async def wx(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not context.args:
        logger.warning(f"Usuario {get_user_display_name(user)} ({user.id}) usó /wx sin argumentos")
        await update.message.reply_text("Debes escribir un indicativo WX. Ejemplo: /wx LU1QA-13")
        return
    
    call = context.args[0]
    log_command(user, f"/wx {call}")
    logger.info(f"Usuario {get_user_display_name(user)} ({user.id}) consultó WX para {call}")
    
    url = f"https://api.aprs.fi/api/get?name={call}&what=wx&apikey={APRS_API_KEY}&format=json"
    r = requests.get(url).json()

    if r.get("entries"):
        wxdata = r["entries"][0]
        msg = (f"Datos meteorológicos {call}:\n"
               f"Temp: {wxdata.get('temp','-')}°C\n"
               f"Humedad: {wxdata.get('humidity','-')}%\n"
               f"Viento: {wxdata.get('wind_speed','-')} km/h")
    else:
        msg = f"No encontré datos WX para {call}."
    
    await update.message.reply_text(msg)

# /ssid
async def ssid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    if not update.message:
        return
        
    if not context.args:
        logger.warning(f"Usuario {get_user_display_name(user)} ({user.id}) usó /ssid sin argumentos")
        await update.message.reply_text("Debes escribir un indicativo base. Ejemplo: /ssid LU1QA")
        return
    
    call = context.args[0]
    log_command(user, f"/ssid {call}")
    logger.info(f"Usuario {get_user_display_name(user)} ({user.id}) consultó SSID para {call}")
    
    try:
        url = f"https://api.aprs.fi/api/get?name={call}&what=loc&apikey={APRS_API_KEY}&format=json"
        r = requests.get(url).json()

        if r.get("entries"):
            ssids = [e["name"] for e in r["entries"]]
            msg = f"📡 *SSID activos para {call}*\n\n"
            msg += "\n".join([f"• {ssid}" for ssid in ssids])
            msg += f"\n\nTotal: {len(ssids)} SSID{'s' if len(ssids) != 1 else ''} encontrado{'s' if len(ssids) != 1 else ''}\n\n"
            msg += f"💡 Usa `/aprs {ssids[0]}` para ver última posición de un SSID específico"
        else:
            msg = f"❌ No encontré SSID activos para {call}.\n\n"
            msg += "Verifica que el indicativo sea correcto."

        await update.message.reply_text(msg, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error en comando ssid: {e}")
        await update.message.reply_text("Error al consultar la API APRS.")

# /telemetria - MEJORADO con TrackDirect
async def telemetry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not context.args:
        logger.warning(f"Usuario {get_user_display_name(user)} ({user.id}) usó /telemetria sin argumentos")
        await update.message.reply_text("Debes escribir un indicativo. Ejemplo: /telemetria LU1QA-1")
        return

    call = context.args[0].upper()
    log_command(user, f"/telemetria {call}")
    logger.info(f"Usuario {get_user_display_name(user)} ({user.id}) consultó telemetría para {call}")

    # Obtener telemetría actual de TrackDirect
    telemetry_data = await tdb.get_station_telemetry(call, limit=1)

    if not telemetry_data:
        await update.message.reply_text(f"❌ No encontré datos de telemetría para {call}.")
        return

    current = telemetry_data[0]

    # Obtener historial para tendencias
    history = await tdb.get_telemetry_history(call, hours=24)

    # Formatear mensaje
    msg = fmt.format_telemetry_message(call, current, history)

    await update.message.reply_text(msg, parse_mode='Markdown')

# /info - NUEVO: Información completa de estación desde TrackDirect
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not context.args:
        logger.warning(f"Usuario {get_user_display_name(user)} ({user.id}) usó /info sin argumentos")
        await update.message.reply_text("Debes escribir un indicativo. Ejemplo: /info LU1QA-1")
        return

    call = context.args[0].upper()
    log_command(user, f"/info {call}")
    logger.info(f"Usuario {get_user_display_name(user)} ({user.id}) consultó info para {call}")

    # Obtener datos de la estación
    station_data = await tdb.get_station_info(call)

    if not station_data:
        await update.message.reply_text(f"❌ No encontré la estación {call}.")
        return

    # Obtener estadísticas
    stats = await tdb.get_station_stats(call)

    # Formatear mensaje
    msg = fmt.format_station_info_message(station_data, stats)

    await update.message.reply_text(msg, parse_mode='Markdown')

# /track - NUEVO: Tracking de posiciones
async def track(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not context.args:
        logger.warning(f"Usuario {get_user_display_name(user)} ({user.id}) usó /track sin argumentos")
        await update.message.reply_text("Debes escribir un indicativo. Ejemplo: /track LU1QA-1")
        return

    call = context.args[0].upper()
    log_command(user, f"/track {call}")
    logger.info(f"Usuario {get_user_display_name(user)} ({user.id}) consultó track para {call}")

    # Obtener últimas 20 posiciones
    positions = await tdb.get_station_positions(call, limit=20)

    if not positions:
        await update.message.reply_text(f"❌ No encontré posiciones para {call}.")
        return

    # Formatear mensaje
    msg = fmt.format_track_message(call, positions)

    await update.message.reply_text(msg, parse_mode='Markdown')

# /cerca - NUEVO: Estaciones cercanas
async def cerca(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not context.args:
        logger.warning(f"Usuario {get_user_display_name(user)} ({user.id}) usó /cerca sin argumentos")
        await update.message.reply_text("Debes escribir un indicativo. Ejemplo: /cerca LU1QA-1")
        return

    call = context.args[0].upper()

    # Radio opcional (default 50km)
    radius = 50
    if len(context.args) > 1:
        try:
            radius = int(context.args[1])
            if radius < 1 or radius > 500:
                await update.message.reply_text("El radio debe estar entre 1 y 500 km.")
                return
        except ValueError:
            await update.message.reply_text("El radio debe ser un número. Ejemplo: /cerca LU1QA-1 100")
            return

    log_command(user, f"/cerca {call} {radius}km")
    logger.info(f"Usuario {get_user_display_name(user)} ({user.id}) consultó estaciones cerca de {call} ({radius}km)")

    # Obtener estación de referencia
    ref_station = await tdb.get_station_info(call)

    if not ref_station:
        await update.message.reply_text(f"❌ No encontré la estación {call}.")
        return

    # Obtener estaciones cercanas
    nearby = await tdb.get_nearby_stations(call, radius_km=radius, limit=15)

    if not nearby:
        await update.message.reply_text(f"❌ No encontré estaciones cerca de {call} en un radio de {radius} km.")
        return

    # Formatear mensaje
    msg = fmt.format_nearby_message(call, ref_station, nearby, radius)

    await update.message.reply_text(msg, parse_mode='Markdown')

# /clima - NUEVO: Datos meteorológicos completos desde TrackDirect
async def clima(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not context.args:
        logger.warning(f"Usuario {get_user_display_name(user)} ({user.id}) usó /clima sin argumentos")
        await update.message.reply_text("Debes escribir un indicativo WX. Ejemplo: /clima LU1QA-13")
        return

    call = context.args[0].upper()
    log_command(user, f"/clima {call}")
    logger.info(f"Usuario {get_user_display_name(user)} ({user.id}) consultó clima para {call}")

    # Obtener datos meteorológicos (últimas 24h para calcular tendencias)
    weather_data = await tdb.get_station_weather(call, limit=50)

    if not weather_data:
        await update.message.reply_text(f"❌ No encontré datos meteorológicos para {call}.")
        return

    # Formatear mensaje
    msg = fmt.format_weather_message(call, weather_data)

    await update.message.reply_text(msg, parse_mode='Markdown')

# /stats (solo para admins) - 🔧 MEJORADO
async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # 🔧 NUEVA VERIFICACIÓN: Múltiples admins
    if not is_admin(user.id):
        await update.message.reply_text("No tienes permisos para usar este comando.")
        return
    
    logger.info(f"Admin {get_user_display_name(user)} ({user.id}) consultó estadísticas")
    
    # Calcular estadísticas
    total_users = len(usage_stats["total_users"])
    total_commands = len(usage_stats["commands_used"])
    uptime = datetime.now(ARGENTINA_TZ) - usage_stats["start_time"]
    
    # Lista de admins configurados
    admin_users = get_admin_users()
    admin_list = ", ".join(admin_users) if admin_users else "Ninguno"
    
    # Últimos 10 comandos
    recent_commands = usage_stats["commands_used"][-10:]
    recent_text = ""
    for cmd in recent_commands:
        # Hora en GMT-3
        cmd_time = datetime.fromisoformat(cmd["timestamp"])
        time_str = cmd_time.strftime("%H:%M:%S")
        
        # Manejo correcto del username
        if cmd.get('username'):
            user_display = f"@{cmd['username']}"
        elif cmd.get('first_name'):
            full_name = cmd['first_name']
            if cmd.get('last_name'):
                full_name += f" {cmd['last_name']}"
            user_display = full_name
        else:
            user_display = f"ID:{cmd['user_id']}"
        
        # Marcar si es admin
        admin_mark = " (ADMIN)" if is_admin(cmd['user_id']) else ""
        
        recent_text += f"• {time_str} - {user_display}{admin_mark}: {cmd['command']}\n"
    
    # Comandos más usados
    command_count = {}
    for cmd in usage_stats["commands_used"]:
        cmd_name = cmd["command"].split()[0]
        command_count[cmd_name] = command_count.get(cmd_name, 0) + 1
    
    popular_commands = sorted(command_count.items(), key=lambda x: x[1], reverse=True)[:5]
    popular_text = ""
    for cmd, count in popular_commands:
        popular_text += f"• {cmd}: {count} veces\n"
    
    # Lista de usuarios únicos
    users_list = ""
    user_count = 0
    for user_id in usage_stats["total_users"]:
        # Buscar el último comando de este usuario
        last_cmd = None
        for cmd in reversed(usage_stats["commands_used"]):
            if cmd["user_id"] == user_id:
                last_cmd = cmd
                break
        
        if last_cmd:
            if last_cmd.get('username'):
                user_display = f"@{last_cmd['username']}"
            elif last_cmd.get('first_name'):
                full_name = last_cmd['first_name']
                if last_cmd.get('last_name'):
                    full_name += f" {last_cmd['last_name']}"
                user_display = full_name
            else:
                user_display = f"ID:{user_id}"
            
            # Marcar si es admin
            admin_mark = " (ADMIN)" if is_admin(user_id) else ""
            users_list += f"• {user_display}{admin_mark}\n"
        else:
            admin_mark = " (ADMIN)" if is_admin(user_id) else ""
            users_list += f"• ID:{user_id}{admin_mark}\n"
        
        user_count += 1
        if user_count >= 10:
            break
    
    stats_message = f"""Estadísticas del Bot APRS

Usuarios únicos: {total_users}
Total comandos: {total_commands}
Tiempo activo: {str(uptime).split('.')[0]}

Administradores: {admin_list}

Comandos más usados:
{popular_text or "Ninguno aún"}

Usuarios activos:
{users_list or "Ninguno aún"}

Últimos 10 comandos:
{recent_text or "Ninguno aún"}
"""
    
    await update.message.reply_text(stats_message)

# /help
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    log_command(user, "/help")
    logger.info(f"Usuario {get_user_display_name(user)} ({user.id}) usó /help")
    
    help_text = (
        "📡 *Bot APRS + TrackDirect - Ayuda*\n\n"
        "*Comandos principales (⭐ TrackDirect):*\n\n"
        "📍 `/info <indicativo>`\n"
        "   Información completa de la estación\n"
        "   Ejemplo: `/info LU1QA-1`\n\n"
        "🚗 `/track <indicativo>`\n"
        "   Tracking de últimas posiciones\n"
        "   Ejemplo: `/track LU1QA-1`\n\n"
        "📍 `/cerca <indicativo> [radio]`\n"
        "   Estaciones cercanas (radio en km, default 50)\n"
        "   Ejemplo: `/cerca LU1QA-1 100`\n\n"
        "🌦️ `/clima <indicativo>`\n"
        "   Datos meteorológicos completos\n"
        "   Ejemplo: `/clima LU1QA-13`\n\n"
        "📊 `/telemetria <indicativo>`\n"
        "   Telemetría con históricos y tendencias\n"
        "   Ejemplo: `/telemetria LU1QA-1`\n\n"
        "*Comandos básicos (aprs.fi):*\n\n"
        "📡 `/aprs <indicativo>` - Última posición\n"
        "🌡️ `/wx <indicativo>` - Datos WX básicos\n"
        "📋 `/ssid <indicativo>` - Lista de SSID activos\n"
    )

    # Agregar comando admin si es admin
    if is_admin(user.id):
        help_text += "\n*Comandos de administrador:*\n\n"
        help_text += "📊 `/stats` - Estadísticas del bot\n"

    help_text += "\n💡 Los comandos marcados con ⭐ usan datos de TrackDirect con históricos y mejor formato."

    await update.message.reply_text(help_text, parse_mode='Markdown')

async def post_init(application: Application) -> None:
    """Inicializa recursos después de crear la aplicación"""
    logger.info("Inicializando pool de conexiones a TrackDirect...")
    await tdb.init_db_pool()
    logger.info("Pool de conexiones inicializado")

async def post_shutdown(application: Application) -> None:
    """Limpia recursos al terminar"""
    logger.info("Cerrando pool de conexiones a TrackDirect...")
    await tdb.close_db_pool()
    logger.info("Pool cerrado")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Configurar callbacks de inicialización y cierre
    app.post_init = post_init
    app.post_shutdown = post_shutdown

    # Registrar handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))

    # Comandos principales con TrackDirect
    app.add_handler(CommandHandler("info", info))
    app.add_handler(CommandHandler("track", track))
    app.add_handler(CommandHandler("cerca", cerca))
    app.add_handler(CommandHandler("clima", clima))
    app.add_handler(CommandHandler("telemetria", telemetry))

    # Comandos básicos con aprs.fi
    app.add_handler(CommandHandler("aprs", aprs))
    app.add_handler(CommandHandler("wx", wx))
    app.add_handler(CommandHandler("ssid", ssid))

    # Comandos admin
    app.add_handler(CommandHandler("stats", stats_cmd))

    print("🚀 Bot APRS en español corriendo...")
    print("📡 Conectado a TrackDirect para datos históricos")
    print("⭐ Nuevos comandos: /info /track /cerca /clima /telemetria")
    app.run_polling()

if __name__ == "__main__":
    main()
