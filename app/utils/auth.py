import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from utils.config import SCOPES, TOKEN_FILE, SERVICE_ACCOUNT_FILE

# Obtener credenciales
if os.path.exists(TOKEN_FILE):
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
else:
    flow = InstalledAppFlow.from_client_secrets_file(
        SERVICE_ACCOUNT_FILE, SCOPES)
    creds = flow.run_local_server(port=0)
    with open(TOKEN_FILE, "w") as token:
        token.write(creds.to_json())

# Crear servicios
gmail_service = build("gmail", "v1", credentials=creds)
drive_service = build("drive", "v3", credentials=creds)
