import os
import requests
import logging
from datetime import datetime, timezone, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

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
        f"Bienvenido al Bot APRS en Español.\n\n"
        f"Tu ID de Telegram es: `{user.id}`\n"
        f"Usuario: {get_user_display_name(user)}{admin_text}\n\n"
        "Experimental - Basado en @APRSBOT\n\n"
        "Comandos disponibles:\n"
        "/aprs <indicativo> → Última posición\n"
        "/wx <indicativo> → Datos meteorológicos\n"
        "/ssid <indicativo> → Lista de SSID\n"
        "/telemetria <indicativo> → Datos de telemetría\n"
        "/help → Ayuda\n"
        f"{'/stats → Estadísticas (solo admin)' if is_admin(user.id) else ''}",
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
            msg = f"SSID activos para {call}: {', '.join(ssids)}"
        else:
            msg = f"No encontré SSID para {call}."
        
        await update.message.reply_text(msg)
        
    except Exception as e:
        logger.error(f"Error en comando ssid: {e}")
        await update.message.reply_text("Error al consultar la API APRS.")

# /telemetria
async def telemetry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not context.args:
        logger.warning(f"Usuario {get_user_display_name(user)} ({user.id}) usó /telemetria sin argumentos")
        await update.message.reply_text("Debes escribir un indicativo. Ejemplo: /telemetria LU1QA-1")
        return
    
    call = context.args[0]
    log_command(user, f"/telemetria {call}")
    logger.info(f"Usuario {get_user_display_name(user)} ({user.id}) consultó telemetría para {call}")
    
    url = f"https://api.aprs.fi/api/get?name={call}&what=telemetry&apikey={APRS_API_KEY}&format=json"
    r = requests.get(url).json()

    if r.get("entries"):
        entry = r["entries"][0]
        vals = entry.get("vals", [])
        bits = entry.get("bits", [])
        msg = (f"Telemetría de {call}:\n"
               f"Voltaje: {vals[0] if len(vals)>0 else '-'} V\n"
               f"Temp: {vals[1] if len(vals)>1 else '-'} °C\n"
               f"Secuencia: {entry.get('seq','-')}\n"
               f"Bits: {bits}")
    else:
        msg = f"No encontré telemetría para {call}."
    
    await update.message.reply_text(msg)

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
        "Comandos disponibles:\n"
        "/aprs <indicativo> → Última posición APRS\n"
        "/wx <indicativo> → Datos meteorológicos\n"
        "/ssid <indicativo> → Lista de SSID usados\n"
        "/telemetria <indicativo> → Datos de telemetría"
    )
    
    # Agregar comando admin si es admin
    if is_admin(user.id):
        help_text += "\n\nComandos de administrador:\n/stats → Estadísticas del bot"
    
    await update.message.reply_text(help_text)

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("aprs", aprs))
    app.add_handler(CommandHandler("wx", wx))
    app.add_handler(CommandHandler("ssid", ssid))
    app.add_handler(CommandHandler("telemetria", telemetry))
    app.add_handler(CommandHandler("stats", stats_cmd))
    
    print("Bot APRS en español corriendo...")
    app.run_polling()

if __name__ == "__main__":
    main()
