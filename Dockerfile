# Usa imagem base enxuta do Python
FROM python:3.11-slim

# Define diretório de trabalho
WORKDIR /code

# Evita geração de pyc e melhora logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/code:${PYTHONPATH}"

# Instala dependências de sistema mínimas (pode ajustar conforme o projeto)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copia dependências primeiro para aproveitar cache
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copia todo o projeto
COPY . .

# Garante permissão de execução do script
RUN chmod +x /code/start-prod.sh

# Railway define a porta dinamicamente via $PORT
EXPOSE $PORT

# Comando de start (usa script para migrations + gunicorn)
CMD ["/code/start-prod.sh"]
