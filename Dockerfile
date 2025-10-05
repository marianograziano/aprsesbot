# Imagen base
FROM python:3.11-slim

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY bot.py .
COPY trackdirect_db.py .
COPY telegram_formatters.py .
COPY stats_web.py .

# Ejecutar
CMD ["python", "bot.py"]
