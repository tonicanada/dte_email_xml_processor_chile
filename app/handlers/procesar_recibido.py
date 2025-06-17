from utils.xml_utils import parsear_xml, renombrar_archivo
from utils.drive_utils import asegurar_carpeta_mes_empresa, subir_a_drive
from utils.gmail_utils import aplicar_etiqueta
from utils.gsheet_utils import registrar_log
from utils.config import EMPRESAS


def reenviar_email_como_original(gmail_service, message_id, destinatario):
    import base64
    from email import policy
    from email.parser import BytesParser

    original = gmail_service.users().messages().get(userId="me", id=message_id, format="raw").execute()
    raw_data = original["raw"]
    raw_bytes = base64.urlsafe_b64decode(raw_data.encode("UTF-8"))

    parsed_msg = BytesParser(policy=policy.SMTP).parsebytes(raw_bytes)
    parsed_msg.replace_header("To", destinatario)
    parsed_msg.replace_header("Subject", f"Fwd: {parsed_msg['Subject']}")

    final_bytes = parsed_msg.as_bytes()
    final_raw = base64.urlsafe_b64encode(final_bytes).decode("utf-8")

    gmail_service.users().messages().send(
        userId="me",
        body={"raw": final_raw}
    ).execute()

    print(f"📨 Mensaje reenviado como original a: {destinatario}")


def procesar_xml_recibido(mensaje, raw_message, xml_path):
    from utils.gmail_utils import gmail_service

    datos = parsear_xml(xml_path)
    empresa = EMPRESAS.get(datos["rut_receptor"])
    if not empresa:
        print(f"Empresa no reconocida: {datos['rut_receptor']}")
        return

    datos["gmail_message_id"] = mensaje["id"]
    nuevo_path = renombrar_archivo(xml_path, datos["fecha_emision"], datos["razon_emisor"])
    datos["nombre_archivo"] = nuevo_path.split("/")[-1]

    aplicar_etiqueta(mensaje["id"], empresa["razon_social"])
    reenviar_email_como_original(gmail_service, mensaje["id"], empresa["email_desis"])

    carpeta_id = asegurar_carpeta_mes_empresa(empresa["carpeta_drive_id"], datos["fecha_emision"], "recibidos")
    drive_id = subir_a_drive(nuevo_path, carpeta_id)
    datos["drive_file_id"] = drive_id

    registrar_log(datos)
    print(f"✅ Recibido procesado: {nuevo_path}")
