import os
import json

SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets"
]

DEFAULT_CRED_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "credenciales")

EMPRESAS_FILE = os.getenv("EMPRESAS_PATH", os.path.join(DEFAULT_CRED_PATH, "empresas.json"))
SERVICE_ACCOUNT_FILE = os.getenv("CREDENTIALS_PATH", os.path.join(DEFAULT_CRED_PATH, "credentials.json"))
TOKEN_FILE = os.getenv("TOKEN_PATH", os.path.join(DEFAULT_CRED_PATH, "token.json"))

GOOGLE_SHEET_ID = "1Vxwhar2lBap84j-WCzAP2vyaNNuzAgkhuZXHgB56ZsA"
CARPETA_TEMP = "xml_descargados"

# Cargar empresas
with open(EMPRESAS_FILE, "r", encoding="utf-8") as f:
    EMPRESAS = json.load(f)


def limpiar_temporales():
    for archivo in os.listdir(CARPETA_TEMP):
        if archivo.lower().endswith(".xml"):
            try:
                os.remove(os.path.join(CARPETA_TEMP, archivo))
                print(f"🧹 Temporal eliminado: {archivo}")
            except Exception as e:
                print(f"⚠️ Error al eliminar {archivo}: {e}")