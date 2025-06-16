# Procesador de XML de Facturas por Email (Chile)

Este proyecto automatiza la recolección, clasificación y archivado de facturas electrónicas (DTE) en formato XML enviadas por email, integrándose con Google Drive y Google Sheets. Está especialmente diseñado para el ecosistema tributario chileno.

---

## 🚀 Características principales

- 📥 Lectura automática de correos electrónicos con XML adjunto desde Gmail
- 🗞️ Identificación de la empresa receptora mediante análisis del XML
- 📨 Reenvío del XML a una casilla de correo según la empresa
- 📁 Subida del XML a una carpeta de Google Drive organizada por empresa y mes
- 🏷️ Etiquetado y archivado del correo original
- 📊 Registro de cada operación en una hoja de cálculo de Google Sheets

---

## 💠 Requisitos

- Cuenta de Google con acceso a:
  - Gmail
  - Google Drive
  - Google Sheets
- Proyecto en Google Cloud con APIs habilitadas:
  - Gmail API
  - Drive API
  - Sheets API
- Archivo `credentials.json` (OAuth de usuario)
- Token de acceso generado (`token.json`)
- Archivo `empresas.json` con configuración por RUT receptor

---

## ⚙ Uso

### 1. Clonar el repositorio

```bash
git clone https://github.com/tuusuario/procesador_dte_email_chile.git
cd procesador_dte_email_chile
```

### 2. Instalar dependencias (opcional si usas Docker)

```bash
pip install -r requirements.txt
```

### 3. Ejecutar

```bash
python procesar_emails.py
```

O bien, si usas Docker:

```bash
./run.sh
```

---

## 🐳 Docker

El proyecto incluye un `Dockerfile` para facilitar su despliegue en servidores como Google Compute Engine.

Los archivos sensibles (`credentials.json`, `token.json`, `empresas.json`) **no se incluyen en la imagen**, y deben ser montados como volumen externo.

---

## 📂 Formato de `empresas.json`

Ejemplo de archivo `empresas.json`:

```json
{
  "77111222-3": {
    "razon_social": "Constructora Los Andes SpA",
    "email_desis": "dteandes@desis.cl",
    "carpeta_drive_id": "id_folder"
  }
}
```

---

## 📈 Logging en Google Sheets

Cada XML procesado se registra en una hoja de cálculo con la siguiente información:

- Fecha de emisión
- RUT y razón social del receptor
- RUT y razón social del emisor
- Folio
- Nombre del archivo
- Fecha de procesamiento
- ID del mensaje de Gmail
- ID del archivo en Google Drive

---

## 📌 Notas

- Los XML se renombran automáticamente con el formato:\
  `yyyymmdd_abreviaturarazonsocial_nombreoriginal.xml`
- Si usas Unidades Compartidas de Google Drive, asegúrate de que el usuario autenticado tenga acceso y se use `supportsAllDrives=True`.

---

## 📄 Licencia

[MIT](LICENSE) — libre para modificar y usar.
