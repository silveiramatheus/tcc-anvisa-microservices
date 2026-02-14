FROM python:3.9-slim

WORKDIR /app

# Dependências do sistema
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expõe a porta que a API vai usar
EXPOSE 8000

# Comando para rodar a API com hot-reload (útil em dev)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]