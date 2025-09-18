# Word Document Processor with LLM

Простая программа для обработки Word документов с помощью языковой модели.

## Установка

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Создайте файл `.env` в корне проекта:
```
API_KEY=your_openrouter_api_key
MODEL_NAME=google/gemma-3-27b-it:free
BASE_URL=https://openrouter.ai/api/v1/chat/completions
```

## Использование

1. Поместите Word документы (.docx) в папку `docs/`

2. Запустите программу:
```bash
python main.py
```

3. Выберите файл из списка и введите промт для обработки

4. Обработанный документ сохранится в папку `new_docs/` с префиксом "new_"

## Структура проекта

```
transform_doc/
├── docs/           # Исходные документы
├── new_docs/       # Обработанные документы
├── logs/           # Логи работы
├── main.py         # Основная программа
├── word_processor.py # Обработка документов
├── llm.py          # Клиент для LLM
├── mylogger.py     # Система логирования
└── requirements.txt # Зависимости
```
