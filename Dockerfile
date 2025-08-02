# Dockerfile (Versão Final com start-prod.sh)
FROM python:3.11-slim
WORKDIR /code

ENV PYTHONPATH "${PYTHONPATH}:/code"

COPY requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . /code

# Garante que os scripts são executáveis DENTRO da imagem
RUN chmod +x /code/start-prod.sh

EXPOSE 8000

# O único comando: execute este script.
CMD ["/code/start-prod.sh"]