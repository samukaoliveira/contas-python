FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    netcat-openbsd  \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

# Porta padrão
EXPOSE 8000

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copia e define entrypoint
COPY entrypoint.sh /entrypoint.sh

# Torna executável (opcional se já fez chmod local)
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

# Comando padrão do container
CMD [ "gunicorn", "controle_gastos.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "5", "--timeout", "120", "--log-level", "info", "--access-logfile", "-", "--error-logfile", "-" ]
