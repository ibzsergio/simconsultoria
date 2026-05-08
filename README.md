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

### Backend en Railway o Render

1. Servicio Python apuntando a carpeta `backend`.
2. Instalar con `pip install -r requirements.txt`.
3. Start command:
   - `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2`
4. Variables de entorno:
   - `DJANGO_SECRET_KEY`
   - `DJANGO_DEBUG=False`
   - `DJANGO_ALLOWED_HOSTS=tu-dominio-backend`
   - `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_DATABASE`, `MYSQL_USER`, `MYSQL_PASSWORD`
   - `CORS_ALLOWED_ORIGINS=https://tu-frontend.netlify.app`
   - **Correo:** en Railway/Netlify Gmail por SMTP suele fallar (`Network unreachable`). Sin `RESEND_API_KEY`/`SENDGRID_*`, el proyecto fuerza **`EMAIL_BACKEND` consola** (el formulario sí guarda; los correos van a logs salvo API). Opcional: `RESEND_API_KEY` + `RESEND_FROM_EMAIL`, o `CONTACT_MAIL_ALLOW_SMTP=1` si tienes SMTP comprobado en el host.
5. Ejecutar migraciones en el entorno:
   - `python manage.py migrate`

## Nota

Si quieres, en el siguiente paso te dejo tambien un guion de evidencia para capturas (checklist para entregar EC0727).
