# Base image com Python
FROM python:3.10

# Instala o htop
RUN apt-get update && apt-get clean

# Configura o diretório de trabalho
WORKDIR /app

# Copia o código do worker para o contêiner
COPY . .

# Instala as dependências
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Comando padrão para executar o worker
CMD ["python", "main.py"]