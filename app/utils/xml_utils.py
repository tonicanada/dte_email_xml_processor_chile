import os
import datetime
import xml.etree.ElementTree as ET


def parsear_xml(path):
    tree = ET.parse(path)
    root = tree.getroot()
    ns = {"d": "http://www.sii.cl/SiiDte"}

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
    tipo_dte = root.findtext(".//d:IdDoc/d:TipoDTE", namespaces=ns)

    return {
        "rut_receptor": rut_recep,
        "razon_social": razon_recep,
        "rut_emisor": rut_emisor,
        "razon_emisor": razon_emisor,
        "folio": folio,
        "fecha_emision": fecha_emision,
        "tipo_dte": tipo_dte
    }


def parsear_resultado_envio(path):
    tree = ET.parse(path)
    root = tree.getroot()

    rut_emisor = root.findtext(".//RUTEMISOR")
    track_id = root.findtext(".//TRACKID")
    fecha_recepcion = root.findtext(".//TMSTRECEPCION")
    estado_envio = root.findtext(".//ESTADO")
    tipo_dte = root.findtext(".//TIPODOC")

    return {
        "rut_emisor": rut_emisor,
        "track_id": track_id,
        "fecha_recepcion": fecha_recepcion,
        "estado_sii": estado_envio,
        "tipo_dte": tipo_dte
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
    nuevo_path = os.path.join(os.path.dirname(path), nuevo_nombre)
    os.rename(path, nuevo_path)
    return nuevo_path
