# Используем официальный Python образ
FROM python:3.11-slim

# Создаем рабочую директорию
WORKDIR /app

# Обновляем pip и устанавливаем зависимости
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir --disable-pip-version-check -r requirements.txt

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
