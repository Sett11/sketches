# Dockerfile для Telegram бота
FROM python:3.11-slim

# Рабочая директория
WORKDIR /app

# Копирование requirements и установка Python зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода бота
COPY . .

# Создание директорий для данных
RUN mkdir -p /app/data/state /app/data/logs

# Запуск бота
CMD ["python", "bot.py"]

