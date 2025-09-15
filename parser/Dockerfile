# Используем официальный Python образ
FROM python:3.11-slim

# Создаем рабочую директорию
WORKDIR /app

# Копируем requirements.txt и устанавливаем зависимости
COPY requirements.txt .
RUN python -m pip install --upgrade pip && python -m pip install --no-cache-dir --disable-pip-version-check -r requirements.txt

# Копируем исходный код
COPY . .

# Создаем необходимые директории
RUN mkdir -p docs logs config

# Устанавливаем переменные окружения
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Открываем порт для Gradio
EXPOSE 7860

# Команда по умолчанию
CMD ["python", "main.py"]
