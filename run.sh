#!/bin/bash

# Ruta donde guardas los archivos sensibles en tu GCE
SECRETS_DIR="/home/antonio/credenciales"

# Ejecutar el contenedor montando los secretos y pasándolos como variables de entorno
docker run --rm \
  -v "$SECRETS_DIR:/app/secretos" \
  -e EMPRESAS_PATH=/app/secretos/empresas.json \
  -e CREDENTIALS_PATH=/app/secretos/credentials.json \
  -e TOKEN_PATH=/app/secretos/token.json \
  procesador-xml