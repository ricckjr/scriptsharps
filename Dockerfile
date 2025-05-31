FROM python:3.12-slim

# Cria diretório de trabalho
WORKDIR /app

# Instala Chrome e dependências do sistema
RUN apt-get update && apt-get install -y \
    curl unzip gnupg ca-certificates fonts-liberation wget \
    libnss3 libxss1 libappindicator3-1 libasound2 libx11-xcb1 libatk-bridge2.0-0 \
    libatk1.0-0 libcups2 libdbus-1-3 libgdk-pixbuf2.0-0 libnspr4 libxcomposite1 \
    libxdamage1 libxrandr2 libgbm1 xdg-utils chromium chromium-driver \
 && rm -rf /var/lib/apt/lists/*

# Instala bibliotecas Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia arquivos do projeto
COPY . .

# Comando principal
CMD ["python", "api.py"]
