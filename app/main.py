from utils.gmail_utils import listar_correos, descargar_xml, es_email_sii, aplicar_etiqueta
from handlers.procesar_recibido import procesar_xml_recibido
from handlers.procesar_envio_sii import procesar_email_envio_sii
import traceback
from utils.config import limpiar_temporales


def main():
    mensajes = listar_correos()
    for mensaje in mensajes:
        try:
            xml_path, raw_message = descargar_xml(mensaje["id"])
            if not xml_path:
                continue

            if es_email_sii(raw_message):
                procesar_email_envio_sii(mensaje, raw_message, xml_path)
            else:
                procesar_xml_recibido(mensaje, raw_message, xml_path)

        except Exception as e:
            print(f"\n❌ Error al procesar mensaje {mensaje['id']}: {e}")
            traceback.print_exc()


if __name__ == "__main__":
    # main()
    limpiar_temporales()
