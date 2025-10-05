"""
Módulo para conexión y consultas a la base de datos de TrackDirect
"""
import os
import asyncpg
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

# Configuración de conexión desde variables de entorno
DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'db'),
    'port': int(os.getenv('POSTGRES_PORT', '5432')),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'trackdirect'),
    'database': os.getenv('POSTGRES_DB', 'trackdirect')
}

# Pool de conexiones global
_pool: Optional[asyncpg.Pool] = None


async def init_db_pool():
    """Inicializa el pool de conexiones a la base de datos"""
    global _pool
    try:
        _pool = await asyncpg.create_pool(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            min_size=2,
            max_size=10,
            command_timeout=60
        )
        logger.info("Pool de conexiones a TrackDirect DB inicializado")
    except Exception as e:
        logger.error(f"Error al inicializar pool de DB: {e}")
        raise


async def close_db_pool():
    """Cierra el pool de conexiones"""
    global _pool
    if _pool:
        await _pool.close()
        logger.info("Pool de conexiones cerrado")


async def get_station_info(callsign: str) -> Optional[Dict[str, Any]]:
    """
    Obtiene información general de una estación

    Returns:
        Dict con: name, lat, lng, symbol, latest_timestamp, comment, etc.
    """
    if not _pool:
        logger.error("Pool de DB no inicializado")
        return None

    query = """
    SELECT
        s.id,
        s.name,
        s.latest_latitude as lat,
        s.latest_longitude as lng,
        s.latest_timestamp,
        s.latest_comment,
        s.latest_symbol,
        s.latest_symbol_table,
        s.latest_course,
        s.latest_speed,
        s.latest_altitude
    FROM station s
    WHERE UPPER(s.name) = UPPER($1)
    ORDER BY s.latest_timestamp DESC
    LIMIT 1
    """

    try:
        async with _pool.acquire() as conn:
            row = await conn.fetchrow(query, callsign)
            if row:
                return dict(row)
            return None
    except Exception as e:
        logger.error(f"Error al obtener info de estación {callsign}: {e}")
        return None


async def get_station_telemetry(callsign: str, limit: int = 1) -> List[Dict[str, Any]]:
    """
    Obtiene telemetría de una estación

    Args:
        callsign: Indicativo de la estación
        limit: Número de registros a retornar

    Returns:
        Lista de dicts con valores de telemetría
    """
    if not _pool:
        logger.error("Pool de DB no inicializado")
        return []

    query = """
    SELECT
        p.timestamp,
        p.telemetry_seq,
        p.telemetry_a1,
        p.telemetry_a2,
        p.telemetry_a3,
        p.telemetry_a4,
        p.telemetry_a5,
        p.telemetry_bits
    FROM packet p
    JOIN station s ON p.station_id = s.id
    WHERE UPPER(s.name) = UPPER($1)
        AND p.telemetry_seq IS NOT NULL
    ORDER BY p.timestamp DESC
    LIMIT $2
    """

    try:
        async with _pool.acquire() as conn:
            rows = await conn.fetch(query, callsign, limit)
            return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al obtener telemetría de {callsign}: {e}")
        return []


async def get_telemetry_history(callsign: str, hours: int = 24) -> List[Dict[str, Any]]:
    """
    Obtiene historial de telemetría de las últimas N horas

    Args:
        callsign: Indicativo de la estación
        hours: Horas hacia atrás

    Returns:
        Lista de registros de telemetría ordenados cronológicamente
    """
    if not _pool:
        logger.error("Pool de DB no inicializado")
        return []

    query = """
    SELECT
        p.timestamp,
        p.telemetry_seq,
        p.telemetry_a1,
        p.telemetry_a2,
        p.telemetry_a3,
        p.telemetry_a4,
        p.telemetry_a5,
        p.telemetry_bits
    FROM packet p
    JOIN station s ON p.station_id = s.id
    WHERE UPPER(s.name) = UPPER($1)
        AND p.telemetry_seq IS NOT NULL
        AND p.timestamp >= NOW() - INTERVAL '$2 hours'
    ORDER BY p.timestamp ASC
    """

    try:
        async with _pool.acquire() as conn:
            rows = await conn.fetch(query, callsign, hours)
            return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al obtener historial de telemetría de {callsign}: {e}")
        return []


async def get_station_positions(callsign: str, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Obtiene últimas posiciones de una estación

    Returns:
        Lista de posiciones con lat, lng, timestamp, speed, course
    """
    if not _pool:
        logger.error("Pool de DB no inicializado")
        return []

    query = """
    SELECT
        p.timestamp,
        p.latitude as lat,
        p.longitude as lng,
        p.speed,
        p.course,
        p.altitude,
        p.comment
    FROM packet p
    JOIN station s ON p.station_id = s.id
    WHERE UPPER(s.name) = UPPER($1)
        AND p.latitude IS NOT NULL
        AND p.longitude IS NOT NULL
    ORDER BY p.timestamp DESC
    LIMIT $2
    """

    try:
        async with _pool.acquire() as conn:
            rows = await conn.fetch(query, callsign, limit)
            return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al obtener posiciones de {callsign}: {e}")
        return []


async def get_station_weather(callsign: str, limit: int = 1) -> List[Dict[str, Any]]:
    """
    Obtiene datos meteorológicos de una estación

    Returns:
        Lista de dicts con datos WX
    """
    if not _pool:
        logger.error("Pool de DB no inicializado")
        return []

    query = """
    SELECT
        p.timestamp,
        p.weather_temperature,
        p.weather_humidity,
        p.weather_pressure,
        p.weather_wind_speed,
        p.weather_wind_gust,
        p.weather_wind_direction,
        p.weather_rain_1h,
        p.weather_rain_24h,
        p.weather_rain_midnight
    FROM packet p
    JOIN station s ON p.station_id = s.id
    WHERE UPPER(s.name) = UPPER($1)
        AND p.weather_temperature IS NOT NULL
    ORDER BY p.timestamp DESC
    LIMIT $2
    """

    try:
        async with _pool.acquire() as conn:
            rows = await conn.fetch(query, callsign, limit)
            return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al obtener datos WX de {callsign}: {e}")
        return []


async def get_station_stats(callsign: str) -> Optional[Dict[str, Any]]:
    """
    Obtiene estadísticas de una estación

    Returns:
        Dict con total_packets, first_heard, last_heard
    """
    if not _pool:
        logger.error("Pool de DB no inicializado")
        return None

    query = """
    SELECT
        COUNT(*) as total_packets,
        MIN(p.timestamp) as first_heard,
        MAX(p.timestamp) as last_heard,
        COUNT(DISTINCT DATE(p.timestamp)) as days_active
    FROM packet p
    JOIN station s ON p.station_id = s.id
    WHERE UPPER(s.name) = UPPER($1)
    """

    try:
        async with _pool.acquire() as conn:
            row = await conn.fetchrow(query, callsign)
            if row:
                return dict(row)
            return None
    except Exception as e:
        logger.error(f"Error al obtener estadísticas de {callsign}: {e}")
        return None


async def get_nearby_stations(callsign: str, radius_km: int = 50, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Obtiene estaciones cercanas a una estación dada

    Args:
        callsign: Indicativo de la estación de referencia
        radius_km: Radio de búsqueda en kilómetros
        limit: Número máximo de estaciones a retornar

    Returns:
        Lista de estaciones cercanas con distancia y dirección
    """
    if not _pool:
        logger.error("Pool de DB no inicializado")
        return []

    query = """
    WITH ref_station AS (
        SELECT latest_latitude as lat, latest_longitude as lng
        FROM station
        WHERE UPPER(name) = UPPER($1)
        LIMIT 1
    )
    SELECT
        s.name,
        s.latest_latitude as lat,
        s.latest_longitude as lng,
        s.latest_timestamp,
        s.latest_symbol,
        s.latest_symbol_table,
        (6371 * acos(
            cos(radians((SELECT lat FROM ref_station))) *
            cos(radians(s.latest_latitude)) *
            cos(radians(s.latest_longitude) - radians((SELECT lng FROM ref_station))) +
            sin(radians((SELECT lat FROM ref_station))) *
            sin(radians(s.latest_latitude))
        )) as distance_km,
        degrees(atan2(
            sin(radians(s.latest_longitude - (SELECT lng FROM ref_station))) * cos(radians(s.latest_latitude)),
            cos(radians((SELECT lat FROM ref_station))) * sin(radians(s.latest_latitude)) -
            sin(radians((SELECT lat FROM ref_station))) * cos(radians(s.latest_latitude)) *
            cos(radians(s.latest_longitude - (SELECT lng FROM ref_station)))
        )) as bearing
    FROM station s
    WHERE UPPER(s.name) != UPPER($1)
        AND s.latest_latitude IS NOT NULL
        AND s.latest_longitude IS NOT NULL
        AND (6371 * acos(
            cos(radians((SELECT lat FROM ref_station))) *
            cos(radians(s.latest_latitude)) *
            cos(radians(s.latest_longitude) - radians((SELECT lng FROM ref_station))) +
            sin(radians((SELECT lat FROM ref_station))) *
            sin(radians(s.latest_latitude))
        )) <= $2
    ORDER BY distance_km ASC
    LIMIT $3
    """

    try:
        async with _pool.acquire() as conn:
            rows = await conn.fetch(query, callsign, radius_km, limit)
            return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al obtener estaciones cercanas a {callsign}: {e}")
        return []
