# -- nome: Dockerfile (sem extensão) --

# Usa Python 3.11 slim (já tem wheel p/ scikit-learn)
FROM python:3.11-slim

# Não rodar prompts interativos
ENV DEBIAN_FRONTEND=noninteractive

# Atualiza pip, setuptools e wheel
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Define diretório de trabalho
WORKDIR /app

# Copia e instala dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código
COPY . .

# Expõe porta
EXPOSE 5000

# Comando de inicialização
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]