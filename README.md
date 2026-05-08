# SIMConsultoria - Vite + Django + MySQL

Proyecto de ejemplo para EC0727: sitio web responsivo para SIMConsultoria con frontend en Vite y backend Django REST conectado a MySQL.

## Contenido requerido EC0727 cubierto

- Iframes: video YouTube y mapa OpenStreetMap.
- Hipervinculos: menu, redes y enlace externo.
- Anclas: navegacion por secciones (`#inicio`, `#contacto`, etc.).
- Tablas: calendario de sesiones.
- Formularios: formulario de contacto conectado a API.
- Multimedia: imagenes, video, audio.
- Apartados solicitados: inicio, sobre nosotros, mision/vision, servicios, clientes, galeria, testimonios, contacto, redes, privacidad y terminos.
- Prueba de funcionamiento: health check visual `GET /api/health/` + envio `POST /api/contacto/`.

## Estructura

- `backend/` Django + DRF + MySQL
- `frontend/` Vite (HTML/CSS/JS)

## 1) Backend (Django + MySQL)

### Requisitos

- Python 3.12+ (o 3.11)
- MySQL 8+

### Preparacion de base

Crear base y usuario en MySQL (ajusta credenciales):

```sql
CREATE DATABASE SIMConsultoria CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'trailuser'@'%' IDENTIFIED BY 'tu_password';
GRANT ALL PRIVILEGES ON SIMConsultoria.* TO 'trailuser'@'%';
FLUSH PRIVILEGES;
```

### Configuracion

1. Entrar a `backend/`
2. Copiar `.env.example` a `.env`
3. Ajustar credenciales MySQL y origenes CORS

### Ejecutar

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

API disponible:

- `GET http://127.0.0.1:8000/api/health/`
- `POST http://127.0.0.1:8000/api/contacto/`
- `http://127.0.0.1:8000/admin/` (ver mensajes)

## 2) Frontend (Vite)

### Ejecutar local

1. Entrar a `frontend/`
2. Instalar dependencias
3. Levantar servidor

```bash
npm install
npm run dev
```

Abre: `http://127.0.0.1:5173`

En desarrollo Vite ya proxea `/api` al backend (`vite.config.js`).

## 3) Pruebas de funcionamiento (evidencia EC0727)

1. Iniciar backend y frontend.
2. Ver indicador en cabecera: debe mostrar `API Django: OK`.
3. Llenar y enviar formulario de contacto.
4. Confirmar mensaje de exito en frontend.
5. Confirmar registro en Django admin (`MensajeContacto`).

## 4) Despliegue sugerido (produccion)

### Frontend en Netlify

1. Conectar repo/carpeta `frontend`.
2. Build command: `npm run build`
3. Publish directory: `dist`
4. Variable de entorno:
   - `VITE_API_URL=https://TU_BACKEND_PUBLICO`
5. Usar `netlify.toml` incluido.

### Backend en Render (recomendado)

1. En Render, usa **Blueprint** e importa el repo (o carpeta) con el archivo `render.yaml`.
2. Render creará:
   - un **Web Service** con Docker (usa `Dockerfile` en la raíz)
   - una **base Postgres**
3. En Render → Web Service → **Environment**:
   - confirma `DJANGO_DEBUG=False`
   - pon `DJANGO_ALLOWED_HOSTS` incluyendo tu host de Render, por ejemplo: `simconsultoria-backend.onrender.com`
   - deja `FRONTEND_ORIGIN=https://simconsultoriaestatica.netlify.app`
   - Render inyecta `DATABASE_URL` cuando conectas la base
4. En Netlify, actualiza el proxy `/api/*` para apuntar al dominio de Render:
   - `https://TU-SERVICIO.onrender.com/api/:splat`
5. Correo:
   - Gmail SMTP en hosting suele fallar (`Network unreachable`). Para entregar EC0727, el formulario guarda y responde OK aun si `EMAIL_FORCE_CONSOLE=1`.
   - Si quieres correos reales, usa `RESEND_API_KEY` + `RESEND_FROM_EMAIL` (recomendado).

## Nota

Si quieres, en el siguiente paso te dejo tambien un guion de evidencia para capturas (checklist para entregar EC0727).
