from django.http import HttpResponse


def inicio_api(request):
    html = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>SIMConsultoria — API</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 40rem; margin: 2rem auto; padding: 0 1rem; line-height: 1.5; }
    a { color: #2563eb; }
    code { background: #f1f5f9; padding: 0.1em 0.35em; border-radius: 4px; }
  </style>
</head>
<body>
  <h1>Backend Django (API)</h1>
  <p>Esta URL es solo el servidor de la API. El sitio web (formulario, secciones) se abre con <strong>Vite</strong>:</p>
  <p><a href="http://127.0.0.1:5173"><code>http://127.0.0.1:5173</code></a></p>
  <p>Enlaces útiles:</p>
  <ul>
    <li><a href="/api/health/">Estado de la API</a> (<code>GET /api/health/</code>)</li>
    <li><a href="/admin/">Administración Django</a></li>
  </ul>
</body>
</html>"""
    return HttpResponse(html)
