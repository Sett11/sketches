# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем системные зависимости и Node.js
RUN set -eux && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    gnupg \
    curl \
    ca-certificates \
    fonts-liberation \
    libayatana-appindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxkbcommon0 \
    libxrandr2 \
    libxshmfence1 \
    libxss1 \
    xdg-utils && \
    # Добавляем GPG ключ NodeSource
    mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && \
    # Добавляем APT репозиторий NodeSource для Node.js 20 LTS
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_20.x nodistro main" > /etc/apt/sources.list.d/nodesource.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Настраиваем переменные окружения для pip и BuildKit кэширования
ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Создаем рабочую директорию
WORKDIR /app

# Копируем requirements.txt и устанавливаем зависимости
COPY requirements.txt .
RUN python -m pip install --upgrade pip && \
    python -m pip install --disable-pip-version-check -r requirements.txt

# Копируем package.json файлы для оптимизации Docker layering
COPY src/core/package*.json ./src/core/

# Устанавливаем Node.js зависимости для Puppeteer
RUN cd /app/src/core && \
    npm install --omit=dev && \
    npx puppeteer browsers install chrome --platform=linux --channel=stable

# Копируем остальной исходный код
COPY . .

# Создаем необходимые директории
RUN mkdir -p docs logs config

# Открываем порт для Gradio
EXPOSE 7860

# Команда по умолчанию
CMD ["python", "main.py"]
