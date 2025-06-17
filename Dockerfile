# Usa una imagen ligera de Python
FROM python:3.11-slim

# Instala dependencias del sistema si es necesario
RUN apt-get update && apt-get install -y \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

# Crea carpeta de trabajo
WORKDIR /app

# Copia la app (sin secretos)
COPY app/ .

# Instala dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Por defecto corre el script
CMD ["python", "main.py"]
