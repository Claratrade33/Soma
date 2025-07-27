# 1. Usa Python 3.11‑slim para garantir wheels pré‑compiladas
FROM python:3.11-slim

# 2. Evita prompts interativos no apt
ENV DEBIAN_FRONTEND=noninteractive

# 3. Atualiza pip, setuptools e wheel
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# 4. Define o diretório de trabalho
WORKDIR /app

# 5. Copia e instala apenas as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copia todo o código da aplicação
COPY . .

# 7. Expõe a porta usada pelo Gunicorn
EXPOSE 5000

# 8. Comando de inicialização com Gunicorn + Eventlet
CMD ["gunicorn", "clara_bunker:app", "--worker-class", "eventlet", "--bind", "0.0.0.0:5000"]
