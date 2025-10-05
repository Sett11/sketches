# Dockerfile для парсера КАДР Арбитр
FROM python:3.11-slim

# Установка базовых утилит и системных зависимостей для Chrome
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    ca-certificates \
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
    && rm -rf /var/lib/apt/lists/*

# Установка Google Chrome (упрощённый метод)
RUN wget -q -O /tmp/google-chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get update \
    && apt-get install -y /tmp/google-chrome.deb \
    && rm /tmp/google-chrome.deb \
    && rm -rf /var/lib/apt/lists/*

# Установка ChromeDriver (автоматическое определение версии)
RUN CHROME_VERSION=$(google-chrome --version | awk '{print $3}') \
    && echo "Chrome version: $CHROME_VERSION" \
    && CHROME_MAJOR=$(echo $CHROME_VERSION | cut -d '.' -f 1) \
    && echo "Chrome major version: $CHROME_MAJOR" \
    && CHROME_MINOR=$(echo $CHROME_VERSION | cut -d '.' -f 2) \
    && echo "Chrome minor version: $CHROME_MINOR" \
    && CHROME_PATCH=$(echo $CHROME_VERSION | cut -d '.' -f 3) \
    && echo "Chrome patch version: $CHROME_PATCH" \
    && CHROMEDRIVER_VERSION="${CHROME_MAJOR}.${CHROME_MINOR}.${CHROME_PATCH}.0" \
    && echo "Looking for ChromeDriver version: $CHROMEDRIVER_VERSION" \
    && wget -q -O /tmp/chromedriver-linux64.zip "https://storage.googleapis.com/chrome-for-testing-public/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip" || \
       (echo "Exact version not found, trying latest for major version $CHROME_MAJOR" && \
        wget -q -O /tmp/chromedriver-linux64.zip "https://storage.googleapis.com/chrome-for-testing-public/${CHROME_MAJOR}.0.0.0/linux64/chromedriver-linux64.zip") || \
       (echo "Fallback to version 131" && \
        wget -q -O /tmp/chromedriver-linux64.zip "https://storage.googleapis.com/chrome-for-testing-public/131.0.6778.87/linux64/chromedriver-linux64.zip") \
    && unzip -q /tmp/chromedriver-linux64.zip -d /tmp/ \
    && mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver \
    && rm -rf /tmp/chromedriver* \
    && chmod +x /usr/local/bin/chromedriver \
    && chromedriver --version

# Рабочая директория
WORKDIR /app

# Копирование requirements и установка Python зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода парсера
COPY . .

# Создание директорий для данных
RUN mkdir -p /app/data/metadata /app/data/pdfs /app/data/state /app/data/logs

# Переменные окружения для Chrome в Docker
ENV DISPLAY=:99
ENV CHROME_BIN=/usr/bin/google-chrome
ENV CHROMEDRIVER_PATH=/usr/local/bin/chromedriver

# Запуск парсера
CMD ["python", "main.py"]

