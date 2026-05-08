FROM python:3.12-slim-bookworm

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

EXPOSE 8000

# `sh` evita problemas de permisos/shebang en Railway/Windows.
ENTRYPOINT ["sh", "/app/docker-entrypoint.sh"]
