# 1. Usa uma imagem oficial do Python em versão leve (slim)
FROM python:3.11-slim

# 2. Define variáveis de ambiente para o Python rodar bem em containers
# PYTHONDONTWRITEBYTECODE: Evita que o Python escreva arquivos .pyc no disco
# PYTHONUNBUFFERED: Garante que os logs saiam no terminal INSTANTANEAMENTE
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_HEADLESS=true

# 3. Define a pasta de trabalho dentro do container
WORKDIR /app

# 4. Instala as dependências do sistema operacional necessárias (se houver)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 5. Copia primeiro o arquivo de dependências (otimiza o cache do Docker)
COPY requirements.txt .

# 6. Instala as bibliotecas Python
RUN pip install --no-cache-dir -r requirements.txt

# 7. Copia o restante do código para dentro do container
COPY . .

# 8. Informa que o container vai rodar na porta padrão do Streamlit
EXPOSE 8501

# 9. Comando para iniciar o Streamlit assim que o container ligar
CMD ["streamlit", "run", "app.py"]
