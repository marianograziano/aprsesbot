"""
Utilidades para formatear datos APRS para Telegram
"""
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
import math

# Zona horaria Argentina
ARGENTINA_TZ = timezone(timedelta(hours=-3))


def format_time_ago(timestamp: datetime) -> str:
    """Formatea un timestamp como 'hace X minutos/horas'"""
    now = datetime.now(timezone.utc)
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)

    diff = now - timestamp

    if diff.total_seconds() < 60:
        return "hace menos de 1 minuto"
    elif diff.total_seconds() < 3600:
        mins = int(diff.total_seconds() / 60)
        return f"hace {mins} minuto{'s' if mins != 1 else ''}"
    elif diff.total_seconds() < 86400:
        hours = int(diff.total_seconds() / 3600)
        return f"hace {hours} hora{'s' if hours != 1 else ''}"
    else:
        days = int(diff.total_seconds() / 86400)
        return f"hace {days} día{'s' if days != 1 else ''}"


def format_timestamp(timestamp: datetime) -> str:
    """Formatea un timestamp en hora Argentina"""
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)

    arg_time = timestamp.astimezone(ARGENTINA_TZ)
    return arg_time.strftime("%d/%m/%Y %H:%M:%S ART")


def create_progress_bar(value: float, min_val: float, max_val: float, length: int = 10) -> str:
    """
    Crea una barra de progreso visual

    Args:
        value: Valor actual
        min_val: Valor mínimo
        max_val: Valor máximo
        length: Longitud de la barra

    Returns:
        String con la barra visual
    """
    if max_val == min_val:
        percentage = 1.0
    else:
        percentage = (value - min_val) / (max_val - min_val)

    percentage = max(0.0, min(1.0, percentage))
    filled = int(percentage * length)
    empty = length - filled

    return "━" * filled + "─" * empty


def format_voltage(voltage: Optional[float], show_bar: bool = True) -> str:
    """Formatea un voltaje con barra de progreso (asumiendo 12V nominal)"""
    if voltage is None:
        return "─"

    if show_bar:
        # Asumiendo sistema 12V: 10.5V = 0%, 14.4V = 100%
        bar = create_progress_bar(voltage, 10.5, 14.4)
        percentage = int(((voltage - 10.5) / (14.4 - 10.5)) * 100)
        percentage = max(0, min(100, percentage))
        return f"{voltage:.1f}V {bar} {percentage}%"
    else:
        return f"{voltage:.1f}V"


def format_temperature(temp: Optional[float]) -> str:
    """Formatea una temperatura"""
    if temp is None:
        return "─"

    # Emojis según temperatura
    if temp < 0:
        emoji = "🥶"
    elif temp < 10:
        emoji = "❄️"
    elif temp < 20:
        emoji = "🌡️"
    elif temp < 30:
        emoji = "☀️"
    else:
        emoji = "🔥"

    return f"{temp:.1f}°C {emoji}"


def format_signal(rssi: Optional[float]) -> str:
    """Formatea RSSI con barra"""
    if rssi is None:
        return "─"

    # RSSI típico: -120 dBm (malo) a -50 dBm (excelente)
    bar = create_progress_bar(rssi, -120, -50)
    percentage = int(((rssi + 120) / 70) * 100)
    percentage = max(0, min(100, percentage))

    if percentage > 80:
        emoji = "📶"
    elif percentage > 50:
        emoji = "📡"
    else:
        emoji = "📊"

    return f"{rssi:.0f} dBm {bar} {percentage}% {emoji}"


def format_bits_status(bits: Optional[int]) -> List[str]:
    """
    Convierte bits de telemetría a estados legibles

    Bits comunes (pueden variar por estación):
    Bit 0: GPS Fix
    Bit 1: TX Enabled
    Bit 2: Low Power Mode
    Bit 3: Sensor 1
    Bit 4: Sensor 2
    Bit 5: Sensor 3
    Bit 6: Sensor 4
    Bit 7: Sensor 5
    """
    if bits is None:
        return []

    statuses = []

    # Bit 0: GPS Fix
    if bits & 0x01:
        statuses.append("✅ GPS Lock")
    else:
        statuses.append("❌ GPS No Fix")

    # Bit 1: TX Enabled
    if bits & 0x02:
        statuses.append("✅ TX ON")
    else:
        statuses.append("❌ TX OFF")

    # Bit 2: Low Power Mode
    if bits & 0x04:
        statuses.append("🔋 Low Power")
    else:
        statuses.append("⚡ Normal Power")

    # Bits 3-7: Sensores genéricos
    for i in range(3, 8):
        if bits & (1 << i):
            statuses.append(f"✅ Sensor {i-2}")

    return statuses


def format_telemetry_trend(values: List[float], show_arrows: bool = True) -> str:
    """
    Genera un mini-gráfico de tendencia ASCII

    Args:
        values: Lista de valores en orden cronológico
        show_arrows: Si mostrar flechas de tendencia

    Returns:
        String con representación visual
    """
    if not values or len(values) < 2:
        return "─"

    # Tomar últimos 5-10 valores
    recent = values[-10:]

    # Crear visualización simple
    visual = " → ".join([f"{v:.1f}" for v in recent[-4:]])

    if show_arrows:
        # Calcular tendencia
        diff = recent[-1] - recent[0]
        if diff > 0.5:
            visual += " ↗️"
        elif diff < -0.5:
            visual += " ↘️"
        else:
            visual += " →"

    return visual


def format_direction(bearing: Optional[float]) -> str:
    """Convierte grados a dirección cardinal"""
    if bearing is None:
        return "─"

    directions = ["N", "NE", "E", "SE", "S", "SO", "O", "NO"]
    index = int((bearing + 22.5) / 45) % 8

    return f"{int(bearing)}° {directions[index]}"


def format_speed(speed: Optional[float]) -> str:
    """Formatea velocidad en km/h"""
    if speed is None:
        return "─"

    if speed < 5:
        emoji = "🚶"  # Caminando
    elif speed < 50:
        emoji = "🚗"  # Coche
    elif speed < 150:
        emoji = "🏎️"  # Rápido
    else:
        emoji = "✈️"  # Avión

    return f"{speed:.0f} km/h {emoji}"


def format_distance(km: float) -> str:
    """Formatea distancia"""
    if km < 1:
        return f"{int(km * 1000)} m"
    else:
        return f"{km:.1f} km"


def get_symbol_emoji(symbol: str, symbol_table: str) -> str:
    """
    Convierte símbolos APRS a emojis

    Args:
        symbol: Caracter del símbolo APRS
        symbol_table: Tabla de símbolos (/ o \\)
    """
    # Mapeo común de símbolos APRS a emojis
    symbol_map = {
        '>': '🚗',  # Coche
        'k': '🚙',  # SUV/Camioneta
        'j': '🚕',  # Jeep
        's': '🚢',  # Barco
        "'": '✈️',  # Avión pequeño
        '^': '🛩️',  # Avión
        '/': '🏠',  # Casa
        '-': '🏡',  # Casa
        'n': '📡',  # Estación fija
        '_': '🌡️',  # Estación meteorológica
        'I': '🏔️',  # Digipeater
        '&': '🗼',  # Gateway/IGate
        'M': '📱',  # Móvil
        'b': '🚲',  # Bicicleta
        '[': '🏃',  # Persona
        'U': '🚌',  # Bus
        'R': '🚐',  # RV
    }

    return symbol_map.get(symbol, '📍')


def format_station_info_message(
    station_data: Dict[str, Any],
    stats: Optional[Dict[str, Any]] = None
) -> str:
    """
    Formatea información completa de una estación para Telegram

    Args:
        station_data: Datos de la estación de la BD
        stats: Estadísticas opcionales

    Returns:
        Mensaje formateado para Telegram
    """
    name = station_data.get('name', 'Desconocido')
    lat = station_data.get('lat')
    lng = station_data.get('lng')
    timestamp = station_data.get('latest_timestamp')
    comment = station_data.get('latest_comment', '')
    symbol = station_data.get('latest_symbol', '')
    symbol_table = station_data.get('latest_symbol_table', '/')
    speed = station_data.get('latest_speed')
    course = station_data.get('latest_course')
    altitude = station_data.get('latest_altitude')

    emoji = get_symbol_emoji(symbol, symbol_table)

    msg = f"📡 *{name}* {emoji}\n\n"

    # Posición
    msg += "📍 *Posición*\n"
    if lat and lng:
        msg += f"├─ Lat: {lat:.4f}°\n"
        msg += f"└─ Lon: {lng:.4f}°\n"
    else:
        msg += "└─ No disponible\n"

    if altitude:
        msg += f"🏔️ Altitud: {int(altitude)} m\n"

    # Movimiento
    if speed is not None or course is not None:
        msg += "\n🚗 *Movimiento*\n"
        if speed is not None:
            msg += f"├─ Velocidad: {format_speed(speed)}\n"
        if course is not None:
            msg += f"└─ Rumbo: {format_direction(course)}\n"

    # Timestamp
    if timestamp:
        msg += f"\n🕐 *Última actualización*\n"
        msg += f"├─ {format_timestamp(timestamp)}\n"
        msg += f"└─ {format_time_ago(timestamp)}\n"

    # Comentario
    if comment:
        msg += f"\n💬 *Comentario*\n"
        msg += f"└─ {comment}\n"

    # Estadísticas
    if stats:
        msg += "\n📊 *Estadísticas*\n"
        total = stats.get('total_packets', 0)
        days = stats.get('days_active', 0)
        first = stats.get('first_heard')

        msg += f"├─ Packets totales: {total}\n"
        msg += f"├─ Días activo: {days}\n"
        if first:
            msg += f"└─ Primera escucha: {format_timestamp(first)}\n"

    return msg


def get_direction_name(bearing: float) -> str:
    """Convierte grados a nombre de dirección en español"""
    directions = [
        ("N", "Norte"),
        ("NE", "Noreste"),
        ("E", "Este"),
        ("SE", "Sureste"),
        ("S", "Sur"),
        ("SO", "Suroeste"),
        ("O", "Oeste"),
        ("NO", "Noroeste")
    ]
    index = int((bearing + 22.5) / 45) % 8
    return directions[index][1]


def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calcula distancia en km entre dos coordenadas usando fórmula de Haversine"""
    from math import radians, cos, sin, asin, sqrt

    lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
    dlat = lat2 - lat1
    dlng = lng2 - lng1

    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
    c = 2 * asin(sqrt(a))
    km = 6371 * c

    return km


def format_track_message(callsign: str, positions: List[Dict[str, Any]]) -> str:
    """
    Formatea tracking de posiciones para Telegram

    Args:
        callsign: Indicativo de la estación
        positions: Lista de posiciones (más reciente primero)

    Returns:
        Mensaje formateado para Telegram
    """
    if not positions:
        return f"❌ No encontré posiciones para {callsign}."

    msg = f"🚗 *Track de {callsign}*\n\n"
    msg += f"📍 *Últimas {len(positions)} posiciones*\n\n"

    total_distance = 0.0
    moving_positions = []

    for i, pos in enumerate(positions[:10]):  # Mostrar máximo 10
        timestamp = pos.get('timestamp')
        lat = pos.get('lat')
        lng = pos.get('lng')
        speed = pos.get('speed')
        course = pos.get('course')
        altitude = pos.get('altitude')

        # Tiempo
        if timestamp:
            time_str = timestamp.astimezone(ARGENTINA_TZ).strftime("%H:%M")
        else:
            time_str = "??"

        # Posición básica
        msg += f"🕐 *{time_str}*"
        if lat and lng:
            msg += f" → ({lat:.4f}°, {lng:.4f}°)\n"
        else:
            msg += " → Sin posición\n"

        # Movimiento
        if speed is not None and speed > 0:
            moving_positions.append(pos)
            msg += f"   🧭 {format_direction(course) if course else '─'} | "
            msg += f"{format_speed(speed)}"
            if altitude:
                msg += f" | 🏔️ {int(altitude)}m"
            msg += "\n"

        # Calcular distancia desde posición anterior
        if i < len(positions) - 1:
            prev = positions[i + 1]
            if lat and lng and prev.get('lat') and prev.get('lng'):
                dist = calculate_distance(
                    prev.get('lat'), prev.get('lng'),
                    lat, lng
                )
                total_distance += dist

        msg += "\n"

    # Resumen
    if len(positions) > 1:
        msg += "📊 *Resumen*\n"

        if total_distance > 0:
            msg += f"├─ 📏 Distancia: {format_distance(total_distance)}\n"

        # Tiempo transcurrido
        first = positions[-1].get('timestamp')
        last = positions[0].get('timestamp')
        if first and last:
            duration = last - first
            hours = int(duration.total_seconds() / 3600)
            minutes = int((duration.total_seconds() % 3600) / 60)
            if hours > 0:
                msg += f"├─ ⏱️ Duración: {hours}h {minutes}m\n"
            else:
                msg += f"├─ ⏱️ Duración: {minutes}m\n"

        # Velocidad promedio
        if moving_positions:
            avg_speed = sum(p.get('speed', 0) for p in moving_positions) / len(moving_positions)
            msg += f"└─ 🏁 Velocidad promedio: {avg_speed:.0f} km/h\n"

    return msg


def format_nearby_message(
    callsign: str,
    ref_position: Dict[str, Any],
    nearby: List[Dict[str, Any]],
    radius_km: int
) -> str:
    """
    Formatea estaciones cercanas para Telegram

    Args:
        callsign: Indicativo de referencia
        ref_position: Posición de referencia
        nearby: Lista de estaciones cercanas
        radius_km: Radio de búsqueda

    Returns:
        Mensaje formateado
    """
    if not nearby:
        return f"❌ No encontré estaciones cerca de {callsign} en un radio de {radius_km} km."

    msg = f"📍 *Estaciones cerca de {callsign}*\n"
    msg += f"Radio de búsqueda: {radius_km} km\n\n"

    for i, station in enumerate(nearby[:15], 1):  # Máximo 15
        name = station.get('name', 'Desconocido')
        distance = station.get('distance_km', 0)
        bearing = station.get('bearing')
        timestamp = station.get('latest_timestamp')
        symbol = station.get('latest_symbol', '')
        symbol_table = station.get('latest_symbol_table', '/')

        emoji = get_symbol_emoji(symbol, symbol_table)

        msg += f"*{i}. {name}* {emoji}\n"

        # Distancia y dirección
        if bearing is not None:
            direction = get_direction_name(bearing)
            msg += f"   📏 {format_distance(distance)} al {direction}\n"
        else:
            msg += f"   📏 {format_distance(distance)}\n"

        # Última actividad
        if timestamp:
            msg += f"   🕐 {format_time_ago(timestamp)}\n"

        msg += "\n"

    msg += f"Total: {len(nearby)} estaciones activas"

    return msg


def format_weather_message(
    callsign: str,
    weather_data: List[Dict[str, Any]]
) -> str:
    """
    Formatea datos meteorológicos completos para Telegram

    Args:
        callsign: Indicativo de la estación WX
        weather_data: Datos meteorológicos

    Returns:
        Mensaje formateado
    """
    if not weather_data:
        return f"❌ No encontré datos meteorológicos para {callsign}."

    current = weather_data[0]
    timestamp = current.get('timestamp')

    msg = f"🌦️ *Estación WX: {callsign}*\n\n"

    # Temperatura
    temp = current.get('weather_temperature')
    if temp is not None:
        msg += "🌡️ *Temperatura*\n"
        msg += f"└─ {format_temperature(temp)}\n\n"

        # Si hay histórico, calcular min/max
        if len(weather_data) > 1:
            temps = [w.get('weather_temperature') for w in weather_data if w.get('weather_temperature') is not None]
            if temps:
                msg += f"   Min/Max hoy: {min(temps):.1f}°C / {max(temps):.1f}°C\n\n"

    # Humedad
    humidity = current.get('weather_humidity')
    if humidity is not None:
        msg += "💧 *Humedad*\n"

        if humidity < 30:
            emoji = "🏜️"
        elif humidity < 60:
            emoji = "☀️"
        elif humidity < 80:
            emoji = "⛅"
        else:
            emoji = "☔"

        msg += f"└─ {humidity:.0f}% {emoji}\n\n"

    # Viento
    wind_speed = current.get('weather_wind_speed')
    wind_gust = current.get('weather_wind_gust')
    wind_dir = current.get('weather_wind_direction')

    if wind_speed is not None:
        msg += "🌬️ *Viento*\n"
        msg += f"├─ Velocidad: {wind_speed:.0f} km/h"

        if wind_dir is not None:
            msg += f" desde {format_direction(wind_dir)}\n"
        else:
            msg += "\n"

        if wind_gust is not None:
            msg += f"└─ Ráfagas: {wind_gust:.0f} km/h\n\n"
        else:
            msg += "\n"

    # Lluvia
    rain_1h = current.get('weather_rain_1h')
    rain_24h = current.get('weather_rain_24h')

    if rain_1h is not None or rain_24h is not None:
        msg += "☔ *Lluvia*\n"
        if rain_1h is not None:
            msg += f"├─ Última hora: {rain_1h:.1f} mm\n"
        if rain_24h is not None:
            msg += f"└─ Últimas 24h: {rain_24h:.1f} mm\n"
        msg += "\n"

    # Presión
    pressure = current.get('weather_pressure')
    if pressure is not None:
        msg += "📊 *Presión atmosférica*\n"

        # Determinar tendencia si hay histórico
        trend = ""
        if len(weather_data) > 1:
            prev_pressure = weather_data[1].get('weather_pressure')
            if prev_pressure:
                diff = pressure - prev_pressure
                if diff > 2:
                    trend = " ↗️ (subiendo)"
                elif diff < -2:
                    trend = " ↘️ (bajando)"
                else:
                    trend = " → (estable)"

        msg += f"└─ {pressure:.1f} hPa{trend}\n\n"

    # Timestamp
    if timestamp:
        msg += "🕐 *Última actualización*\n"
        msg += f"└─ {format_time_ago(timestamp)}\n"

    return msg


def format_telemetry_message(
    callsign: str,
    current: Dict[str, Any],
    history: Optional[List[Dict[str, Any]]] = None
) -> str:
    """
    Formatea mensaje de telemetría completo

    Args:
        callsign: Indicativo de la estación
        current: Datos actuales de telemetría
        history: Historial opcional para tendencias

    Returns:
        Mensaje formateado para Telegram
    """
    msg = f"📊 *Telemetría {callsign}*\n\n"

    a1 = current.get('telemetry_a1')
    a2 = current.get('telemetry_a2')
    a3 = current.get('telemetry_a3')
    a4 = current.get('telemetry_a4')
    a5 = current.get('telemetry_a5')
    bits = current.get('telemetry_bits')
    seq = current.get('telemetry_seq')
    timestamp = current.get('timestamp')

    # Canales analógicos
    msg += "🔋 *Alimentación*\n"
    if a1 is not None:
        msg += f"├─ Batería: {format_voltage(a1)}\n"
    if a4 is not None:
        msg += f"└─ Panel solar: {format_voltage(a4, show_bar=False)}\n"

    msg += "\n🌡️ *Sensores*\n"
    if a2 is not None:
        msg += f"├─ Temperatura: {format_temperature(a2)}\n"
    if a3 is not None:
        msg += f"└─ Señal RSSI: {format_signal(a3)}\n"

    # Bits digitales
    if bits is not None:
        msg += "\n💾 *Sistema*\n"
        statuses = format_bits_status(bits)
        for i, status in enumerate(statuses):
            prefix = "├─" if i < len(statuses) - 1 else "└─"
            msg += f"{prefix} {status}\n"

    # Tendencias
    if history and len(history) > 1:
        msg += "\n📈 *Tendencia (últimas 24h)*\n"

        # Voltaje
        voltages = [h.get('telemetry_a1') for h in history if h.get('telemetry_a1') is not None]
        if voltages:
            msg += f"├─ Batería: {format_telemetry_trend(voltages)}\n"

        # Temperatura
        temps = [h.get('telemetry_a2') for h in history if h.get('telemetry_a2') is not None]
        if temps:
            msg += f"└─ Temp: {format_telemetry_trend(temps)}\n"

    # Info de secuencia
    msg += "\n📡 *Última actualización*\n"
    if seq is not None:
        msg += f"├─ Secuencia: #{seq:,}\n"
    if timestamp:
        msg += f"├─ {format_timestamp(timestamp)}\n"
        msg += f"└─ {format_time_ago(timestamp)}\n"

    return msg
