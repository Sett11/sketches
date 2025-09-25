#!/bin/bash

echo "Запуск OpenWebUI с Pipelines и MCPO..."

# Проверка наличия .env файла
if [ ! -f .env ]; then
    echo "Создайте файл .env с переменными окружения"
    exit 1
fi

# Загрузка переменных окружения
source .env

# Запуск всех сервисов
docker-compose up -d

echo "Развёртывание завершено!"
echo "OpenWebUI: http://localhost:${OPENWEBUI_PORT:-3000}"
echo "Pipelines: http://localhost:${PIPELINES_PORT:-9099}"
echo "MCPO: http://localhost:${MCPO_PORT:-8000}"
echo "Jur-MCPO: http://localhost:${JUR_MCPO_PORT:-8001}"
echo ""
echo "Для просмотра логов: docker-compose logs -f"