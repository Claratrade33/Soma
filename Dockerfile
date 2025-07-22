# Usa Python 3.11 (slim) para garantir wheels pré-compiladas
FROM python:3.11-slim

# Não pedir interação em instalações
ENV DEBIAN_FRONTEND=noninteractive

# Atualiza pip, setuptools e wheel
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Define diretório de trabalho
WORKDIR /app

# Copia apenas o requirements para agilizar cache do Docker
COPY requirements.txt .

# Instala as deps
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código
COPY . .

# Expõe a porta que o Gunicorn vai usar
EXPOSE 5000

# Roda o Gunicorn apontando para app:app
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]