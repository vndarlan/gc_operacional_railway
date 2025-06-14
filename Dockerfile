FROM python:3.10-slim

# Define variável de ambiente para indicar que estamos no Railway
ENV RAILWAY_ENVIRONMENT=true
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV SELENIUM_TIMEOUT=60

# Instala dependências do sistema e Chrome em uma única layer
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    unzip \
    bash \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libwayland-client0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libglib2.0-0 \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Configura diretório de trabalho
WORKDIR /app

# Copia arquivos de requisitos
COPY requirements.txt .

# Instala todas as dependências Python de uma vez com versões atualizadas
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    numpy==1.24.4 \
    pandas==2.0.3 \
    streamlit==1.39.0 \
    selenium==4.17.2 \
    webdriver-manager==4.0.1 \
    apscheduler==3.10.4 \
    psycopg2-binary \
    beautifulsoup4==4.12.2 \
    plotly==5.15.0 \
    python-dotenv==1.0.1 \
    sqlalchemy==2.0.27

# Copia o restante dos arquivos
COPY . .

# Cria diretórios necessários e define permissões
RUN mkdir -p /app/logs /app/screenshots \
    && touch /app/dropi_automation.db \
    && chmod -R 777 /app/logs /app/screenshots \
    && chmod 666 /app/dropi_automation.db

# Expõe a porta que será usada
EXPOSE 8080

# Comando para executar a aplicação
CMD streamlit run iniciar.py --server.address=0.0.0.0 --server.port=${PORT:-8080}