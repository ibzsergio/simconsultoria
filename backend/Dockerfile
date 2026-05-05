FROM python:3.12-slim-bookworm

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["/bin/sh", "-c", "echo \"Running migrations...\" && python manage.py migrate --noinput && echo \"Starting gunicorn...\" && exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2"]
