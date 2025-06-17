import os
from googleapiclient.http import MediaFileUpload
from utils.auth import drive_service


def asegurar_carpeta_mes_empresa(empresa_drive_id, fecha_emision, tipo):
    mes = fecha_emision[:7]
    # Buscar carpeta del mes
    query_mes = f"'{empresa_drive_id}' in parents and name = '{mes}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    res_mes = drive_service.files().list(q=query_mes, fields="files(id)",
                                         supportsAllDrives=True, includeItemsFromAllDrives=True).execute()
    carpeta_mes_id = res_mes["files"][0]["id"] if res_mes["files"] else None

    if not carpeta_mes_id:
        folder_metadata = {
            "name": mes,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [empresa_drive_id],
        }
        folder = drive_service.files().create(body=folder_metadata, fields="id",
                                              supportsAllDrives=True).execute()
        carpeta_mes_id = folder["id"]

    # Buscar subcarpeta recibidos/enviados
    query_tipo = f"'{carpeta_mes_id}' in parents and name = '{tipo}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    res_tipo = drive_service.files().list(q=query_tipo, fields="files(id)",
                                          supportsAllDrives=True, includeItemsFromAllDrives=True).execute()
    carpeta_tipo_id = res_tipo["files"][0]["id"] if res_tipo["files"] else None

    if not carpeta_tipo_id:
        folder_metadata = {
            "name": tipo,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [carpeta_mes_id],
        }
        folder = drive_service.files().create(body=folder_metadata, fields="id",
                                              supportsAllDrives=True).execute()
        carpeta_tipo_id = folder["id"]

    return carpeta_tipo_id


def archivo_ya_existe(nombre_archivo, folder_id):
    query = f"'{folder_id}' in parents and name = '{nombre_archivo}' and trashed = false"
    resultados = drive_service.files().list(
        q=query,
        spaces='drive',
        fields="files(id, name)",
        supportsAllDrives=True,
        includeItemsFromAllDrives=True
    ).execute()
    archivos = resultados.get("files", [])
    return archivos[0]["id"] if archivos else None


def subir_a_drive(path, folder_id):
    nombre_archivo = os.path.basename(path)
    existente_id = archivo_ya_existe(nombre_archivo, folder_id)

    if existente_id:
        print(f"⚠️ Ya existe en Drive: {nombre_archivo}, no se sube de nuevo.")
        return existente_id

    file_metadata = {"name": nombre_archivo, "parents": [folder_id]}
    media = MediaFileUpload(path, resumable=True)
    file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id",
        supportsAllDrives=True
    ).execute()
    return file["id"]
