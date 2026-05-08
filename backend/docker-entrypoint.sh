#!/usr/bin/env sh
set -eu

# Migraciones + gunicorn con reintentos (Railway/DB a veces tarda en estar lista).
PORT="${PORT:-8000}"
echo "[entrypoint] PORT=${PORT}"

attempt=1
ok=0
while [ "$attempt" -le 30 ]; do
  if python manage.py migrate --noinput; then
    echo "[entrypoint] migrate OK (intento ${attempt})"
    ok=1
    break
  fi
  echo "[entrypoint] migrate falló (intento ${attempt}/30), reintento en 3s…"
  sleep 3
  attempt=$((attempt + 1))
done

if [ "$ok" -ne 1 ]; then
  echo "[entrypoint] ERROR: migrate no terminó bien tras ${attempt} intentos"
  exit 1
fi

echo "[entrypoint] gunicorn…"
exec gunicorn config.wsgi:application \
  --bind "0.0.0.0:${PORT}" \
  --workers "${WEB_CONCURRENCY:-2}" \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -

