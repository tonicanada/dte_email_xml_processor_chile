from utils.config import GOOGLE_SHEET_ID
from utils.auth import creds
import gspread
import datetime

gsheet = gspread.authorize(creds)


def registrar_log(datos):
    hoja = gsheet.open_by_key(GOOGLE_SHEET_ID).sheet1
    encabezado = [
        "Fecha Emisión", "Tipo DTE", "Estado SII", "Track ID", "RUT Receptor", "Razón Social",
        "RUT Emisor", "Razón Emisor", "Folio", "Nombre Archivo",
        "Fecha Procesamiento", "ID Gmail", "ID Archivo Drive"
    ]
    primera_fila = hoja.row_values(1)
    if not primera_fila or primera_fila != encabezado:
        hoja.insert_row(encabezado, index=1)

    fila = [
        datos.get("fecha_emision", ""),
        datos.get("tipo_dte", ""),
        datos.get("estado_sii", ""),
        datos.get("track_id", ""),
        datos.get("rut_receptor", ""),
        datos.get("razon_social", ""),
        datos.get("rut_emisor", ""),
        datos.get("razon_emisor", ""),
        datos.get("folio", ""),
        datos.get("nombre_archivo", ""),
        datetime.datetime.now().isoformat(),
        datos.get("gmail_message_id", ""),
        datos.get("drive_file_id", "")
    ]
    hoja.append_row(fila, value_input_option="USER_ENTERED")
    print("📝 Log agregado al Google Sheet.")
