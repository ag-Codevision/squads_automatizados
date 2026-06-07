FROM python:3.12-slim

# Instalar FFmpeg e dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalação das bibliotecas Python da esteira do orquestrador
RUN pip install --no-cache-dir \
    requests \
    supabase \
    elevenlabs \
    python-dotenv \
    google-auth-oauthlib \
    google-api-python-client

# Copiar os arquivos do código-fonte
COPY . .

# Comando padrão (executar o orquestrador)
CMD ["python", "scripts/orquestrador.py"]
