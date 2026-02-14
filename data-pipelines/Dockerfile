FROM python:3.9-slim

WORKDIR /app

# Instala compiladores necessários
RUN apt-get update && apt-get install -y libpq-dev gcc curl && rm -rf /var/lib/apt/lists/*

# Instala bibliotecas
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Configura o Python para achar seus módulos na pasta src
ENV PYTHONPATH=/app/src

CMD ["python", "src/main.py"]