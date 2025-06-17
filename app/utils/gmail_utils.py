import os
import base64
from utils.auth import gmail_service
from utils.config import CARPETA_TEMP


os.makedirs(CARPETA_TEMP, exist_ok=True)


def listar_correos():
    query = "label:INBOX filename:xml"
    response = gmail_service.users().messages().list(userId="me", q=query).execute()
    return response.get("messages", [])


def descargar_xml(message_id):
    message = gmail_service.users().messages().get(userId="me", id=message_id).execute()
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


def es_email_sii(message):
    headers = message.get("payload", {}).get("headers", [])
    remitente = next((h["value"] for h in headers if h["name"] == "From"), "")
    asunto = next((h["value"] for h in headers if h["name"] == "Subject"), "")
    return "siidte@sii.cl" in remitente.lower() and "Resultado de Revision Envio" in asunto


def aplicar_etiqueta(message_id, etiqueta):
    labels = gmail_service.users().labels().list(userId="me").execute().get("labels", [])
    label_id = None
    for l in labels:
        if l["name"].lower() == etiqueta.lower():
            label_id = l["id"]
            break
    if not label_id:
        label = gmail_service.users().labels().create(userId="me", body={"name": etiqueta}).execute()
        label_id = label["id"]

    gmail_service.users().messages().modify(
        userId="me",
        id=message_id,
        body={"addLabelIds": [label_id], "removeLabelIds": ["INBOX"]}
    ).execute()
