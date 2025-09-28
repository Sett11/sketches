#!/bin/bash

echo "🚀 ТЕСТИРОВАНИЕ DOCUMENT TRANSFORM PIPELINE"
echo "=========================================="

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функции для логирования
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Проверяем, что мы на хосте
if [ -f "/app/backend/main.py" ]; then
    error "Этот скрипт должен запускаться на хосте, а не в контейнере!"
    exit 1
fi

log "Начинаем тестирование Document Transform Pipeline..."

# 1. Проверяем Docker
log "Проверяем Docker..."
if ! command -v docker &> /dev/null; then
    error "Docker не установлен!"
    exit 1
fi
success "Docker доступен"

# 2. Проверяем контейнеры
log "Проверяем статус контейнеров..."
CONTAINERS=$(docker ps --format "table {{.Names}}\t{{.Status}}" | grep -E "(open-webui|pipelines)")

if echo "$CONTAINERS" | grep -q "open-webui"; then
    success "Контейнер open-webui запущен"
else
    error "Контейнер open-webui НЕ запущен!"
    echo "Запустите: docker-compose up -d"
    exit 1
fi

if echo "$CONTAINERS" | grep -q "pipelines"; then
    success "Контейнер pipelines запущен"
else
    error "Контейнер pipelines НЕ запущен!"
    echo "Запустите: docker-compose up -d"
    exit 1
fi

# 3. Проверяем доступность Pipelines API
log "Проверяем доступность Pipelines API..."
if curl -s -H "Authorization: Bearer 0p3n-w3bu!" http://localhost:9099/v1/ > /dev/null 2>&1; then
    success "Pipelines API доступен"
else
    error "Pipelines API НЕ доступен"
    echo "Проверьте, что контейнер pipelines запущен и порт 9099 открыт"
    exit 1
fi

# 4. Проверяем доступные модели
log "Проверяем доступные модели..."
MODELS_RESPONSE=$(curl -s -w "HTTPSTATUS:%{http_code}" \
    -H "Authorization: Bearer 0p3n-w3bu!" \
    http://localhost:9099/v1/models 2>/dev/null)

MODELS_STATUS=$(echo $MODELS_RESPONSE | sed -e "s/.*HTTPSTATUS://")
MODELS_BODY=$(echo $MODELS_RESPONSE | sed -e "s/HTTPSTATUS:.*//g")

if [ "$MODELS_STATUS" = "200" ]; then
    success "Модели доступны (статус: $MODELS_STATUS)"
    echo "Доступные модели:"
    echo "$MODELS_BODY" | jq -r '.data[] | "  - \(.id) (\(.name))"' 2>/dev/null || echo "$MODELS_BODY" | head -c 300
    echo "..."
    
    # Сохраняем имя модели для дальнейшего использования
    log "Пытаемся извлечь имя модели..."
    AVAILABLE_MODEL=$(echo "$MODELS_BODY" | jq -r '.data[0].id' 2>/dev/null)
    log "Результат jq: '$AVAILABLE_MODEL'"
    
    if [ "$AVAILABLE_MODEL" != "null" ] && [ -n "$AVAILABLE_MODEL" ]; then
        log "Используем модель: $AVAILABLE_MODEL"
    else
        # Если jq не работает, извлекаем вручную
        log "jq не сработал, извлекаем вручную..."
        AVAILABLE_MODEL=$(echo "$MODELS_BODY" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
        log "Результат ручного извлечения: '$AVAILABLE_MODEL'"
        
        if [ -n "$AVAILABLE_MODEL" ]; then
            log "Используем модель (извлечена вручную): $AVAILABLE_MODEL"
        else
            error "Не удалось определить доступную модель"
            echo "Полный ответ API:"
            echo "$MODELS_BODY"
            echo ""
            echo "Попробуем альтернативный способ..."
            # Альтернативный способ извлечения
            AVAILABLE_MODEL="transform_doc"  # Модель называется transform_doc
            log "Используем модель по умолчанию: $AVAILABLE_MODEL"
        fi
    fi
else
    error "Модели НЕ доступны (статус: $MODELS_STATUS)"
    echo "Ответ: $MODELS_BODY"
    exit 1
fi

# 5. Проверяем загрузку pipeline в контейнере
log "Проверяем загрузку pipeline в контейнере pipelines..."

# Проверяем, что файл transform_doc.py существует
if docker exec pipelines ls -la /app/custom_pipelines/transform_doc.py > /dev/null 2>&1; then
    success "Файл transform_doc.py найден в контейнере"
else
    error "Файл transform_doc.py НЕ найден в контейнере!"
    echo "Содержимое /app/custom_pipelines/:"
    docker exec pipelines ls -la /app/custom_pipelines/
    exit 1
fi

# Проверяем импорт pipeline
log "Проверяем импорт pipeline..."
PIPELINE_TEST=$(docker exec pipelines python3 -c "
import sys
sys.path.append('/app/custom_pipelines')
try:
    from transform_doc import Pipeline
    print('✅ Pipeline импортируется')
    p = Pipeline()
    print('✅ Pipeline создается')
    print('SUCCESS')
except Exception as e:
    print(f'❌ Ошибка: {e}')
    print('ERROR')
" 2>/dev/null)

if echo "$PIPELINE_TEST" | grep -q "SUCCESS"; then
    success "Pipeline импортируется и создается"
else
    error "Pipeline НЕ импортируется"
    echo "Результат теста:"
    echo "$PIPELINE_TEST"
    exit 1
fi

# 6. Тестируем простой API запрос
log "Тестируем простой API запрос..."

# Создаем тестовый запрос с правильным именем модели
cat > /tmp/api_test.json << APIEOF
{
    "model": "$AVAILABLE_MODEL",
    "messages": [{"role": "user", "content": "Привет! Это тест."}],
    "stream": false
}
APIEOF

# Показываем, что именно отправляется
log "Отправляемый JSON:"
cat /tmp/api_test.json
echo ""

API_RESPONSE=$(curl -s -w "HTTPSTATUS:%{http_code}" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer 0p3n-w3bu!" \
    -X POST \
    -d @/tmp/api_test.json \
    http://localhost:9099/v1/chat/completions 2>/dev/null)

API_STATUS=$(echo $API_RESPONSE | sed -e "s/.*HTTPSTATUS://")
API_BODY=$(echo $API_RESPONSE | sed -e "s/HTTPSTATUS:.*//g")

if [ "$API_STATUS" = "200" ]; then
    success "API запрос успешен (статус: $API_STATUS)"
    echo "Ответ API:"
    echo "$API_BODY" | jq -r '.choices[0].message.content' 2>/dev/null || echo "$API_BODY" | head -c 200
    echo "..."
else
    error "API запрос неудачен (статус: $API_STATUS)"
    echo "Ответ: $API_BODY"
fi

# 7. Тестируем с файлом (если это Document Transform Pipeline)
log "Тестируем обработку файла..."

# Создаем тестовый Word документ
python3 -c "
from docx import Document
doc = Document()
doc.add_paragraph('Hello World Test Document')
doc.save('/tmp/test.docx')
print('Word документ создан')
" 2>/dev/null || echo "Не удалось создать Word документ"

# Кодируем Word документ в base64
base64 -w 0 /tmp/test.docx > /tmp/test_base64.txt
FILE_DATA=$(cat /tmp/test_base64.txt)

# Создаем JSON с файлом
cat > /tmp/file_test.json << FILEEOF
{
    "model": "$AVAILABLE_MODEL",
    "messages": [{"role": "user", "content": "Обработай документ"}],
    "file_data": "$FILE_DATA",
    "prompt": "Добавь восклицательный знак в конец",
    "filename": "test.docx",
    "stream": false
}
FILEEOF

# Показываем, что именно отправляется для файлового теста
log "Отправляемый JSON для файлового теста:"
cat /tmp/file_test.json
echo ""

FILE_RESPONSE=$(curl -s -w "HTTPSTATUS:%{http_code}" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer 0p3n-w3bu!" \
    -X POST \
    -d @/tmp/file_test.json \
    http://localhost:9099/v1/chat/completions 2>/dev/null)

FILE_STATUS=$(echo $FILE_RESPONSE | sed -e "s/.*HTTPSTATUS://")
FILE_BODY=$(echo $FILE_RESPONSE | sed -e "s/HTTPSTATUS:.*//g")

if [ "$FILE_STATUS" = "200" ]; then
    success "Запрос с файлом успешен (статус: $FILE_STATUS)"
    echo "Ответ с файлом:"
    echo "$FILE_BODY" | jq -r '.choices[0].message.content' 2>/dev/null || echo "$FILE_BODY" | head -c 200
    echo "..."
    
    # Проверяем, создался ли файл в папке docs
    log "Проверяем, создался ли файл в папке docs:"
    docker exec pipelines ls -la /app/docs/ 2>/dev/null || echo "Папка docs пуста или не существует"
    
    # Проверяем содержимое файла
    log "Проверяем содержимое файла:"
    docker exec pipelines cat /app/docs/20250928_203320_test.txt 2>/dev/null || echo "Не удалось прочитать файл"
    
    # Проверяем, существует ли файл по абсолютному пути
    log "Проверяем существование файла по абсолютному пути:"
    docker exec pipelines ls -la /app/docs/20250928_203320_test.txt 2>/dev/null || echo "Файл не найден по абсолютному пути"
    
    # Проверяем права доступа к файлу
    log "Проверяем права доступа к файлу:"
    docker exec pipelines stat /app/docs/20250928_203320_test.txt 2>/dev/null || echo "Не удалось получить информацию о файле"
    
    # Проверяем, создался ли файл в папке new_docs
    log "Проверяем, создался ли файл в папке new_docs:"
    docker exec pipelines ls -la /app/new_docs/ 2>/dev/null || echo "Папка new_docs пуста или не существует"
    
    # Проверяем права доступа к файлу
    log "Проверяем права доступа к файлу:"
    docker exec pipelines ls -la /app/docs/20250928_202741_test.txt 2>/dev/null || echo "Файл не найден"
else
    warning "Запрос с файлом неудачен (статус: $FILE_STATUS)"
    echo "Ответ: $FILE_BODY"
fi

# 8. Проверяем логи на ошибки
log "Проверяем логи на ошибки..."
echo "=== ЛОГИ PIPELINES (последние 10 строк) ==="
docker logs --tail 10 pipelines 2>/dev/null | grep -i error || echo "Ошибок в логах pipelines не найдено"

# 9. Итоговый отчет
echo ""
echo "======================================"
echo "🎯 ИТОГОВЫЙ ОТЧЕТ ТЕСТИРОВАНИЯ"
echo "======================================"

# Проверяем статус контейнеров
echo "Статус контейнеров:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "(open-webui|pipelines)"

echo ""
echo "📊 РЕЗУЛЬТАТЫ ТЕСТОВ:"

if echo "$PIPELINE_TEST" | grep -q "SUCCESS"; then
    success "✅ Pipeline импортируется"
else
    error "❌ Pipeline НЕ импортируется"
fi

if [ "$MODELS_STATUS" = "200" ]; then
    success "✅ Модели доступны"
else
    error "❌ Модели НЕ доступны"
fi

if [ "$API_STATUS" = "200" ]; then
    success "✅ API работает"
else
    error "❌ API НЕ работает"
fi

if [ "$FILE_STATUS" = "200" ]; then
    success "✅ Обработка файлов работает"
else
    warning "⚠️ Обработка файлов НЕ работает (возможно, не поддерживается)"
fi

echo ""
echo "🔧 ПОЛЕЗНЫЕ КОМАНДЫ ДЛЯ ОТЛАДКИ:"
echo "docker logs -f pipelines          # Логи pipelines в реальном времени"
echo "docker logs -f open-webui         # Логи open-webui в реальном времени"
echo "docker exec -it pipelines bash    # Войти в контейнер pipelines"
echo "docker exec -it open-webui bash   # Войти в контейнер open-webui"
echo "docker-compose restart pipelines  # Перезапустить pipelines"
echo "docker-compose restart open-webui  # Перезапустить open-webui"

echo ""
echo "🔍 ДОПОЛНИТЕЛЬНАЯ ДИАГНОСТИКА:"
echo "=================================="

# Проверяем статус Pipelines API
log "Проверяем статус Pipelines API..."
curl -s -H "Authorization: Bearer 0p3n-w3bu!" http://localhost:9099/v1/ | head -c 200
echo ""

# Проверяем pipelines endpoint
log "Проверяем pipelines endpoint..."
curl -s -H "Authorization: Bearer 0p3n-w3bu!" http://localhost:9099/pipelines | head -c 200
echo ""

# Проверяем valves spec для pipeline
log "Проверяем valves spec для pipeline..."
curl -s -H "Authorization: Bearer 0p3n-w3bu!" http://localhost:9099/pipeline/valves/spec | head -c 200
echo ""

# Проверяем логи pipelines на предмет ошибок
log "Проверяем логи pipelines на предмет ошибок..."
docker logs pipelines 2>&1 | grep -i error | tail -5 || echo "Ошибок в логах не найдено"

# Проверяем переменные окружения в контейнере pipelines
log "Проверяем переменные окружения в pipelines..."
docker exec pipelines env | grep -E "(OPENROUTER|MODEL|PIPELINES)" || echo "Переменные не найдены"

# Проверяем структуру файлов в pipelines
log "Структура файлов в pipelines:"
docker exec pipelines ls -la /app/custom_pipelines/

# Проверяем папки docs и new_docs
log "Проверяем папки docs и new_docs:"
docker exec pipelines ls -la /app/docs/ 2>/dev/null || echo "Папка docs не существует"
docker exec pipelines ls -la /app/new_docs/ 2>/dev/null || echo "Папка new_docs не существует"

# Создаем папки если их нет
log "Создаем папки docs и new_docs:"
docker exec pipelines mkdir -p /app/docs /app/new_docs
docker exec pipelines ls -la /app/ | grep -E "(docs|new_docs)"

# Проверяем импорт pipeline вручную
log "Проверяем импорт pipeline вручную..."
docker exec pipelines python3 -c "
import sys
sys.path.append('/app/custom_pipelines')
try:
    from transform_doc import Pipeline
    print('✅ Pipeline импортируется')
    p = Pipeline()
    print('✅ Pipeline создается')
    print('✅ Pipeline готов к работе')
    
    # Тестируем простой запрос
    result = p.pipe('Тест', 'transform_doc', [{'role': 'user', 'content': 'Тест'}], {})
    print(f'✅ Тестовый запрос: {result}')
    
    # Создаем тестовый Word документ
    from docx import Document
    doc = Document()
    doc.add_paragraph('Hello World Test Document')
    doc.save('/tmp/test_internal.docx')
    print('Word документ создан для теста')
    
    # Кодируем в base64
    import base64
    with open('/tmp/test_internal.docx', 'rb') as f:
        test_file_data = base64.b64encode(f.read()).decode('utf-8')
    
    # Тестируем с файлом
    result_with_file = p.pipe('Обработай документ', 'transform_doc', [{'role': 'user', 'content': 'Обработай документ'}], {
        'file_data': test_file_data,
        'prompt': 'Добавь восклицательный знак в конец',
        'filename': 'test.docx'
    })
    print(f'✅ Тестовый запрос с файлом: {result_with_file}')
    
    # Проверяем, что происходит с файлом в Python
    import os
    test_file_path = '/app/docs/20250928_203320_test.txt'
    print(f'Проверяем файл: {test_file_path}')
    print(f'Файл существует: {os.path.exists(test_file_path)}')
    if os.path.exists(test_file_path):
        print(f'Размер файла: {os.path.getsize(test_file_path)} байт')
        with open(test_file_path, 'r') as f:
            content = f.read()
            print(f'Содержимое файла: {repr(content)}')
except Exception as e:
    print(f'❌ Ошибка: {e}')
    import traceback
    traceback.print_exc()
"

# Очищаем временные файлы
rm -f /tmp/api_test.json /tmp/file_test.json /tmp/test.txt /tmp/test_base64.txt

log "Тестирование завершено!"