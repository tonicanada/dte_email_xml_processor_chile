import os
import base64
import json
import datetime
import xml.etree.ElementTree as ET
import mimetypes

from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import gspread

# --- Configuración ---
SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets"
]

DEFAULT_CRED_PATH = os.path.join(
    os.path.dirname(__file__), "..", "credenciales")


EMPRESAS_FILE = os.getenv("EMPRESAS_PATH", os.path.join(
    DEFAULT_CRED_PATH, "empresas.json"))
SERVICE_ACCOUNT_FILE = os.getenv(
    "CREDENTIALS_PATH", os.path.join(DEFAULT_CRED_PATH, "credentials.json"))
TOKEN_FILE = os.getenv("TOKEN_PATH", os.path.join(
    DEFAULT_CRED_PATH, "token.json"))
GOOGLE_SHEET_ID = "1Vxwhar2lBap84j-WCzAP2vyaNNuzAgkhuZXHgB56ZsA"
CARPETA_TEMP = "xml_descargados"

# --- Autenticación OAuth Usuario ---
if os.path.exists(TOKEN_FILE):
    creds = Credentials.from_authorized_user_file(
        TOKEN_FILE, SCOPES)
else:
    flow = InstalledAppFlow.from_client_secrets_file(
        SERVICE_ACCOUNT_FILE, SCOPES)
    creds = flow.run_local_server(port=0)
    with open("token.json", "w") as token:
        token.write(creds.to_json())

gmail_service = build("gmail", "v1", credentials=creds)
drive_service = build("drive", "v3", credentials=creds)
gsheet = gspread.authorize(creds)

# --- Cargar configuración ---
with open(EMPRESAS_FILE, "r", encoding="utf-8") as f:
    EMPRESAS = json.load(f)

os.makedirs(CARPETA_TEMP, exist_ok=True)

# --- Funciones ---


def listar_correos():
    query = "label:INBOX filename:xml"
    response = gmail_service.users().messages().list(userId="me", q=query).execute()
    return response.get("messages", [])


def descargar_xml(message_id):
    message = gmail_service.users().messages().get(
        userId="me", id=message_id).execute()
    parts = message["payload"].get("parts", [])
    for part in parts:
        filename = part.get("filename")
        if filename and filename.lower().endswith(".xml"):
            attach_id = part["body"]["attachmentId"]
            data = gmail_service.users().messages().attachments().get(
                userId="me", messageId=message_id, id=attach_id
            ).execute()["data"]
            file_data = base64.urlsafe_b64decode(data.encode("UTF-8"))
            path = os.path.join(CARPETA_TEMP, filename)
            with open(path, "wb") as f:
                f.write(file_data)
            return path, message
    return None, None


def parsear_xml(path):
    tree = ET.parse(path)
    root = tree.getroot()
    ns = {"d": "http://www.sii.cl/SiiDte"}

    # Probar primero la ruta clásica del sobre de envío (Caratula)
    rut_recep = root.findtext(".//d:Caratula/d:RUTRecep", namespaces=ns)
    razon_recep = root.findtext(".//d:Caratula/d:RznSocRecep", namespaces=ns)

    if not rut_recep:
        rut_recep = root.findtext(".//d:Receptor/d:RUTRecep", namespaces=ns)
        razon_recep = root.findtext(
            ".//d:Receptor/d:RznSocRecep", namespaces=ns)

    rut_emisor = root.findtext(".//d:Emisor/d:RUTEmisor", namespaces=ns)
    razon_emisor = root.findtext(".//d:Emisor/d:RznSoc", namespaces=ns)
    folio = root.findtext(".//d:IdDoc/d:Folio", namespaces=ns)
    fecha_emision = root.findtext(".//d:IdDoc/d:FchEmis", namespaces=ns)

    return {
        "rut_receptor": rut_recep,
        "razon_social": razon_recep,
        "rut_emisor": rut_emisor,
        "razon_emisor": razon_emisor,
        "folio": folio,
        "fecha_emision": fecha_emision
    }


def abreviar_razon_social(razon_social):
    return (
        razon_social.lower()
        .replace(" ", "").replace(".", "").replace(",", "")
        .replace("á", "a").replace("é", "e").replace("í", "i")
        .replace("ó", "o").replace("ú", "u")
    )[:15]


def renombrar_archivo(path, fecha_emision, razon_social):
    nombre_original = os.path.basename(path)
    fecha_prefix = datetime.datetime.strptime(
        fecha_emision, "%Y-%m-%d").strftime("%Y%m%d")
    abreviado = abreviar_razon_social(razon_social)
    nuevo_nombre = f"{fecha_prefix}_{abreviado}_{nombre_original}"
    nuevo_path = os.path.join(CARPETA_TEMP, nuevo_nombre)
    os.rename(path, nuevo_path)
    return nuevo_path


def aplicar_etiqueta(message_id, etiqueta):
    labels = gmail_service.users().labels().list(
        userId="me").execute().get("labels", [])
    label_id = None
    for l in labels:
        if l["name"].lower() == etiqueta.lower():
            label_id = l["id"]
            break
    if not label_id:
        label = gmail_service.users().labels().create(
            userId="me", body={"name": etiqueta}).execute()
        label_id = label["id"]
    gmail_service.users().messages().modify(
        userId="me",
        id=message_id,
        body={"addLabelIds": [label_id], "removeLabelIds": ["INBOX"]}
    ).execute()


def reenviar_email_como_original(message_id, destinatario):
    # Obtener el mensaje original como raw
    original = gmail_service.users().messages().get(
        userId="me",
        id=message_id,
        format="raw"
    ).execute()

    raw_data = original["raw"]
    raw_bytes = base64.urlsafe_b64decode(raw_data.encode("UTF-8"))

    # Parsear el mensaje original y cambiar el destinatario
    import email
    from email import policy
    from email.parser import BytesParser

    parsed_msg = BytesParser(policy=policy.SMTP).parsebytes(raw_bytes)
    parsed_msg.replace_header("To", destinatario)
    parsed_msg.replace_header("Subject", f"Fwd: {parsed_msg['Subject']}")

    # Reconvertir a base64url
    final_bytes = parsed_msg.as_bytes()
    final_raw = base64.urlsafe_b64encode(final_bytes).decode("utf-8")

    gmail_service.users().messages().send(
        userId="me",
        body={"raw": final_raw}
    ).execute()

    print(f"📨 Mensaje reenviado como original a: {destinatario}")


def registrar_log(datos, gsheet, GOOGLE_SHEET_ID):
    hoja = gsheet.open_by_key(GOOGLE_SHEET_ID).sheet1
    encabezado = [
        "Fecha Emisión", "RUT Receptor", "Razón Social", "RUT Emisor",
        "Razón Emisor", "Folio", "Nombre Archivo", "Fecha Procesamiento",
        "ID Gmail", "ID Archivo Drive"
    ]
    primera_fila = hoja.row_values(1)
    if not primera_fila or primera_fila != encabezado:
        hoja.insert_row(encabezado, index=1)

    fila = [
        datos["fecha_emision"], datos["rut_receptor"], datos["razon_social"],
        datos["rut_emisor"], datos["razon_emisor"], datos["folio"],
        datos["nombre_archivo"], datetime.datetime.now().isoformat(),
        datos.get("gmail_message_id", ""), datos.get("drive_file_id", "")
    ]
    hoja.append_row(fila, value_input_option="USER_ENTERED")
    print("📝 Log agregado al Google Sheet.")


def limpiar_temporales():
    for archivo in os.listdir(CARPETA_TEMP):
        if archivo.endswith(".xml"):
            try:
                os.remove(os.path.join(CARPETA_TEMP, archivo))
            except Exception as e:
                print(f"⚠️ Error al borrar {archivo}: {e}")


def main():
    mensajes = listar_correos()
    for mensaje in mensajes:
        try:
            xml_path, _ = descargar_xml(mensaje["id"])
            if not xml_path:
                continue

            datos = parsear_xml(xml_path)
            empresa = EMPRESAS.get(datos["rut_receptor"])
            if not empresa:
                print(f"Empresa no reconocida: {datos['rut_receptor']}")
                continue

            datos["gmail_message_id"] = mensaje["id"]
            nuevo_path = renombrar_archivo(
                xml_path, datos["fecha_emision"], datos["razon_emisor"])
            datos["nombre_archivo"] = os.path.basename(nuevo_path)

            aplicar_etiqueta(mensaje["id"], empresa["razon_social"])
            reenviar_email_como_original(mensaje["id"], empresa["email_desis"])

            # Subir a Google Drive
            subcarpeta = datos["fecha_emision"][:7]
            query = f"'{empresa['carpeta_drive_id']}' in parents and name = '{subcarpeta}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
            res = drive_service.files().list(q=query, fields="files(id)",
                                             supportsAllDrives=True, includeItemsFromAllDrives=True).execute()
            folders = res.get("files", [])
            if folders:
                subfolder_id = folders[0]["id"]
            else:
                folder_metadata = {
                    "name": subcarpeta,
                    "mimeType": "application/vnd.google-apps.folder",
                    "parents": [empresa["carpeta_drive_id"]],
                }
                folder = drive_service.files().create(
                    body=folder_metadata,
                    fields="id",
                    supportsAllDrives=True
                ).execute()
                subfolder_id = folder["id"]

            file_metadata = {"name": os.path.basename(
                nuevo_path), "parents": [subfolder_id]}
            media = MediaFileUpload(nuevo_path, resumable=True)
            file = drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields="id",
                supportsAllDrives=True
            ).execute()

            datos["drive_file_id"] = file["id"]
            registrar_log(datos, gsheet, GOOGLE_SHEET_ID)

            print(f"✅ Procesado: {nuevo_path}")

        except Exception as e:
            print(f"❌ Error al procesar {mensaje['id']}: {e}")


if __name__ == "__main__":
    main()
    limpiar_temporales()
