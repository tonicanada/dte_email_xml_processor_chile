import os
import base64
from utils.xml_utils import parsear_resultado_envio, renombrar_archivo
from utils.drive_utils import asegurar_carpeta_mes_empresa, subir_a_drive
from utils.gmail_utils import aplicar_etiqueta
from utils.gsheet_utils import registrar_log
from utils.config import EMPRESAS, CARPETA_TEMP


def procesar_email_envio_sii(mensaje, raw_message, path_uno):
    from utils.gmail_utils import gmail_service

    # Extraer empresa desde remitente del XML
    datos = parsear_resultado_envio(path_uno)
    empresa = EMPRESAS.get(datos["rut_emisor"])
    if not empresa:
        print(f"Empresa no reconocida (SII): {datos['rut_emisor']}")
        return

    datos["gmail_message_id"] = mensaje["id"]
    fecha = datos.get("fecha_recepcion", "")[:10]
    if "/" in fecha:
        partes = fecha.split(" ")[0].split("/")
        datos["fecha_emision"] = f"{partes[2]}-{partes[1]}-{partes[0]}"
    else:
        datos["fecha_emision"] = fecha

    # Renombrar y subir ambos XML adjuntos
    parts = raw_message["payload"].get("parts", [])
    xml_paths = []

    for part in parts:
        filename = part.get("filename")
        if filename and filename.lower().endswith(".xml"):
            attach_id = part["body"]["attachmentId"]
            data = gmail_service.users().messages().attachments().get(
                userId="me", messageId=mensaje["id"], id=attach_id
            ).execute()["data"]
            file_data = base64.urlsafe_b64decode(data.encode("UTF-8"))
            full_path = os.path.join(CARPETA_TEMP, filename)
            with open(full_path, "wb") as f:
                f.write(file_data)
            xml_paths.append(full_path)

    carpeta_id = asegurar_carpeta_mes_empresa(empresa["carpeta_drive_id"], datos["fecha_emision"], "enviados")
    for path in xml_paths:
        nuevo_path = renombrar_archivo(path, datos["fecha_emision"], empresa["razon_social"])
        datos["nombre_archivo"] = os.path.basename(nuevo_path)
        datos["drive_file_id"] = subir_a_drive(nuevo_path, carpeta_id)
        registrar_log(datos)

    aplicar_etiqueta(mensaje["id"], empresa["razon_social"])
    print(f"📤 Email del SII procesado y etiquetado para empresa {empresa['razon_social']}")
