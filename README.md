# Procesador de XML de Facturas por Email (Chile)

Este proyecto automatiza la recolección, clasificación y archivado de facturas electrónicas (DTE) en formato XML enviadas por email, integrándose con Google Drive y Google Sheets. Está especialmente diseñado para el ecosistema tributario chileno y soporta tanto documentos recibidos como respuestas del SII.

---

## 🚀 Características principales

- 📅 Lectura automática de correos electrónicos con XML adjunto desde Gmail
- 📄 Distinción automática entre:
  - Documentos recibidos de proveedores (con EnvioDTE)
  - Respuestas del SII con resultado de validación (emails desde `siidte@sii.cl`)
- 🗾️ Identificación de la empresa mediante análisis del XML
- 📨 Reenvío del XML a la casilla asociada a la empresa
- 📁 Subida a Google Drive, organizado por empresa, mes y tipo (`recibidos/` o `enviados/`)
- 🏇 Etiquetado automático del correo con la empresa y salida de la bandeja de entrada
- 📊 Registro detallado de cada operación en Google Sheets

---

## 🛀 Requisitos

- Cuenta de Google con acceso a:
  - Gmail
  - Google Drive
  - Google Sheets
- Proyecto en Google Cloud con APIs habilitadas:
  - Gmail API
  - Drive API
  - Sheets API
- Archivos requeridos:
  - `credentials.json` (OAuth usuario)
  - `token.json` (generado al autenticar)
  - `empresas.json` (configuración por RUT receptor)

---

## ⚙ Uso

### 1. Clonar el repositorio

```bash
git clone https://github.com/tuusuario/procesador_dte_email_chile.git
cd procesador_dte_email_chile
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Ejecutar

```bash
python xml_processor/main.py
```

---

## 🐳 Docker

Incluye `Dockerfile` listo para Google Compute Engine, Cloud Run o servidores Linux.

> 🛑 **Los archivos **``**, **``**, **``** deben montarse desde fuera del contenedor.**

---

## 📂 Formato de `empresas.json`

```json
{
  "76407152-2": {
    "razon_social": "Constructora Andes Spa",
    "email_desis": "facturas@tecton.cl",
    "carpeta_drive_id": "abc123456..."
  }
}
```

---

## 📈 Logging en Google Sheets

Cada XML procesado se registra en una hoja con columnas:

- Fecha de emisión
- Tipo DTE (33, 52, etc)
- Estado del SII (solo en respuestas)
- RUT y Razón Social del receptor
- RUT y Razón Social del emisor
- Folio
- Nombre de archivo
- Fecha de procesamiento
- ID del mensaje Gmail
- ID del archivo en Google Drive

---

## 📌 Notas

- Los XML se renombran con el formato:\
  `yyyymmdd_abreviaturarazonsocial_nombreoriginal.xml`
- En Drive, los archivos se almacenan en:\
  `empresa/mes/recibidos/` o `empresa/mes/enviados/`
- Se usa `supportsAllDrives=True` para compatibilidad con unidades compartidas

---

## 📄 Licencia

[MIT](LICENSE) — libre para modificar y reutilizar.
