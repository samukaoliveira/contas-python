#!/bin/sh

echo "Aplicando migrações..."
python manage.py migrate --noinput

echo "Criando pasta de arquivos estáticos..."
mkdir -p /app/staticfiles

echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

echo "Iniciando Gunicorn..."
exec "$@"
