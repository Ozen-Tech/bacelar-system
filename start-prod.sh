#!/bin/bash
set -e

# As migrações agora rodam aqui, antes de tudo.
echo "==> [start-prod.sh] Executando migrações do banco de dados..."
alembic upgrade head

# O servidor Gunicorn é iniciado
echo "==> [start-prod.sh] Iniciando o servidor Gunicorn..."
gunicorn -w 3 -k uvicorn.workers.UvicornWorker \
  --forwarded-allow-ips='*' \
  app.main:app \
  --bind 0.0.0.0:$PORT
