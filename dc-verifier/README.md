# DCV (Data Chains Verifier)

Инструмент для проверки целостности цепочек данных между слоями приложения (Frontend → Backend → Database) **БЕЗ ЗАПУСКА приложения**.

## Концепция

DCV анализирует поток данных через граф вызовов:
1. Находит точку входа (main.py, app.py для Python; .ts/.tsx файлы для TypeScript)
2. Строит граф вызовов: отслеживает импорты → функции → классы → методы
3. Извлекает схемы данных (Pydantic модели, Zod схемы, TypeScript интерфейсы)
4. Идет по графу: main → route → handler → crud → model
5. Отслеживает поток данных через граф
6. Проверяет контракты на каждом стыке
7. Формирует отчет о несоответствиях

## Возможности

- ✅ **Поддержка Python/FastAPI** - парсинг Python кода, извлечение FastAPI routes, Pydantic моделей
- ✅ **Поддержка TypeScript** - парсинг TypeScript кода, извлечение импортов, вызовов, функций, классов, методов, Zod схем, интерфейсов и type aliases
- ✅ **Построение графов вызовов** - автоматическое построение графа для Python и TypeScript проектов
- ✅ **Отслеживание потока данных** - отслеживание параметров и возвращаемых значений через граф
- ✅ **Проверка контрактов** - проверка соответствия схем данных на стыках цепочек
- ✅ **Визуализация графов** - генерация DOT формата для визуализации графов вызовов
- ✅ **Кэширование** - сохранение и загрузка графов для ускорения повторных проверок
- ✅ **Гибкая конфигурация** - поддержка множественных адаптеров и правил проверки

## Установка

```bash
cargo build --release
```

Бинарный файл будет находиться в `target/release/dc-verifier`.

## Использование

### Инициализация конфига

```bash
dc-verifier init
```

Создаст файл `dc-verifier.toml` с примером конфигурации.

### Проверка цепочек

```bash
# Markdown формат (по умолчанию)
dc-verifier check

# JSON формат
dc-verifier check --format json
```

Проверяет цепочки данных согласно конфигурации и генерирует отчет в формате Markdown или JSON.

### Визуализация графов

```bash
dc-verifier visualize
```

Генерирует DOT файлы для визуализации графов вызовов. Файлы можно открыть в Graphviz или онлайн-инструментах.

## Структура проекта

- `crates/dc-core/` - Ядро: построение графов, анализ потока данных, парсеры, анализаторы
- `crates/dc-adapter-fastapi/` - Адаптер для FastAPI (Python)
- `crates/dc-typescript/` - Адаптер для TypeScript
- `crates/dc-cli/` - CLI инструмент

## Конфигурация

Пример конфигурации для проекта с Python/FastAPI и TypeScript:

```toml
project_name = "my-project"

# Maximum recursion depth (optional, None = unlimited)
# max_recursion_depth = 100

[output]
format = "markdown"  # или "json"
path = "dc-verifier-report.md"

[[adapters]]
adapter_type = "fastapi"
app_path = "app/main.py"

[[adapters]]
adapter_type = "typescript"
src_paths = ["frontend/src", "shared"]
```

### Адаптеры

#### FastAPI адаптер

```toml
[[adapters]]
adapter_type = "fastapi"
app_path = "app/main.py"  # Путь к файлу с FastAPI приложением
```

#### TypeScript адаптер

```toml
[[adapters]]
adapter_type = "typescript"
src_paths = ["src", "lib"]  # Директории с TypeScript файлами
```

### Правила проверки

```toml
[rules]
type_mismatch = "warning"      # Проверка несоответствия типов
missing_field = "critical"     # Проверка отсутствующих полей
unnormalized_data = "warning"  # Проверка нормализации данных
```

## Примеры использования

### Python/FastAPI проект

```bash
# 1. Создать конфигурацию
dc-verifier init

# 2. Настроить dc-verifier.toml
# Указать путь к FastAPI приложению

# 3. Запустить проверку
dc-verifier check

# 4. Просмотреть отчет
cat dc-verifier-report.md
```

### TypeScript проект

```bash
# 1. Создать конфигурацию
dc-verifier init

# 2. Настроить dc-verifier.toml
# Указать директории с TypeScript файлами

# 3. Запустить проверку
dc-verifier check

# 4. Визуализировать граф
dc-verifier visualize
# Открыть сгенерированный .dot файл в Graphviz
```

### Смешанный проект (Python + TypeScript)

```toml
project_name = "fullstack-app"

[[adapters]]
adapter_type = "fastapi"
app_path = "backend/app/main.py"

[[adapters]]
adapter_type = "typescript"
src_paths = ["frontend/src"]
```

## Что проверяется

DCV проверяет следующие аспекты цепочек данных:

1. **Соответствие типов** - проверяет, что типы данных совпадают на стыках цепочек
2. **Обязательные поля** - проверяет, что все обязательные поля присутствуют
3. **Нормализация данных** - проверяет валидацию (email, URL, паттерны)

## Форматы отчетов

- **Markdown** (по умолчанию) - человекочитаемый формат с эмодзи и форматированием
  - Использование: `dc-verifier check` или `dc-verifier check --format markdown`
- **JSON** - машинночитаемый формат для интеграции с другими инструментами
  - Использование: `dc-verifier check --format json`

## Требования

- Rust 1.70+
- Python 3.8+ (для FastAPI адаптера)
- Node.js (не требуется, но может быть полезен для TypeScript проектов)

## Статус проекта

Проект готов к использованию. Текущая готовность: **~98-100%**.

### Реализовано

- ✅ Парсинг Python и TypeScript кода
- ✅ Построение графов вызовов для Python и TypeScript
- ✅ Извлечение функций, классов и методов из TypeScript AST
- ✅ Извлечение TypeScript интерфейсов и type aliases
- ✅ Связывание Zod схем с TypeScript типами
- ✅ Парсинг TypeScript схем в JsonSchema
- ✅ Отслеживание потока данных
- ✅ Проверка контрактов
- ✅ Визуализация графов
- ✅ Кэширование графов
- ✅ CLI интерфейс
- ✅ Валидация конфигурации с детальными сообщениями об ошибках
- ✅ Ограничение глубины рекурсии для больших проектов
- ✅ Прогресс-бар для длительных операций
- ✅ JSON формат отчетов (опция `--format json`)
- ✅ Улучшенная обработка ошибок (thiserror)
- ✅ Unit и integration тесты (32 теста, все проходят)

### В планах

- ⚠️ Улучшение документации (примеры использования)

## Лицензия

См. файл LICENSE (или Cargo.toml для информации о лицензии).

## Контрибуция

Проект открыт для контрибуций! См. детали в коде и документации.
