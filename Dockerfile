FROM python:3.12-slim

# Variáveis de ambiente recomendadas
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Diretório de trabalho
WORKDIR /app

# Dependências de sistema (psycopg)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements
COPY requirements.txt .

# Instala dependências Python
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copia o projeto
COPY . .

# Coleta arquivos estáticos (opcional, mas recomendado)
RUN python manage.py collectstatic --noinput

# Porta padrão do Django/Gunicorn
EXPOSE 8000

# Comando de produção
CMD ["gunicorn", "controle_gastos.wsgi:application", "--bind", "0.0.0.0:8000"]
