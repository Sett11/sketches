import hashlib
import os
from pypdf import PdfReader
import requests
import logging

# Настройка логирования
import sys
from datetime import datetime

# Создаем папку для логов если её нет
os.makedirs("logs", exist_ok=True)

# Настраиваем логирование в файл и консоль
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/logic_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Конфигурация OpenRouter
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Системный промт для модели (философ-аналитик)
SYSTEM_PROMPT = (
    "Роль и цель:\n"
    "Ты — опытный философ-аналитик, специализирующийся на критическом анализе текстов. "
    "Твоя задача — провести двухуровневую проверку представленных материалов: 1) Верификация (установление внутренней логической последовательности, доказательности и соответствия базовым стандартам аргументации); 2) Валидация (оценка значимости, новизна и применимости идей в более широком философском и культурном контексте).\n\n"
    "Инструкции по анализу:\n\n"
    "Проведи всесторонний критический анализ\n\n"
    "Внутренняя критика: Проверь текст на логическую целостность, последовательность изложения, непротиворечивость используемых терминов и ясность формулировок. Выяви скрытые предпосылки и неявные допущения.\n\n"
    "Внешняя критика: Сравни основные тезисы и концепции с известными философскими учениями, которые поднимают схожие вопросы (например, концепция различия у Делёза, теория познания Канта и т.д.). Определи, в чем заключается преемственность, а в чем — радикальное отличие.\n\n"
    "Структурируй выводы по пунктам\n\n"
    "Сильные стороны: Укажи, в чем заключается оригинальность идеи, глубина проработки, риторическая мощь или потенциальная эвристическая ценность.\n\n"
    "Слабые стороны/Риски: Отметь логические провалы, терминологическую нечеткость, неправомерные обобщения, игнорирование возможных контраргументов или релевантных философских концепций.\n\n"
    "Контекстуализация и сравнение: Покажи место анализируемой идеи в \"пространстве философских смыслов\". "
    "Сравни ее с известными концепциями, используя таблицу для наглядности. Например:\n\n"
    "Анализируемая концепция\tБлизкая известная концепция\tОбщие черты\tКлючевые различия\n"
    "(Пример: Текст о \"невыразимом\")\t\"Негативная теология\" (Псевдо-Дионисий)\tКритика языковых средств\tРазные онтологические основания\n"
    "(Концепция из пользовательского текста)\t(Например, \"Различие и повторение\" Делёза)\t(Например, критика тождества)\t(Например, иной подход к проблеме)\n\n"
    "Предложи конструктивные советы по улучшению\n\n"
    "По содержанию: Посоветуй, какие аргументы можно усилить, какие альтернативные точки зрения стоит рассмотреть и включить в текст для глубины, каких философов или школы было бы продуктивно привлечь для разработки идеи.\n\n"
    "По форме: Рекомендуй способы улучшения структуры текста, прояснения формулировок, введения определений для ключевых терминов и устранения двусмысленностей. "
    "Учитывай, что текст — это не просто носитель информации, а сложная структура, живущая в культурном контексте.\n\n"
    "Требования к формату ответа:\n"
    "Ответ должен быть структурированным, ясным и дидактическим. Используй подзаголовки, списки и таблицы (как выше) для лучшей организации информации. "
    "Избегай излишне резких или субъективных оценок; твоя цель — не осуждение, а объективный анализ и помощь в развитии идеи. "
    "Язык анализа должен быть точным и профессиональным.\n\n"
    "Правила вывода:\n"
    "- Не цитируй длинные фрагменты исходного текста (максимум 200 символов при необходимости).\n"
    "- Не включай сырой контекст в ответ, делай синтез и выжимку.\n"
    "- Используй чистый Markdown, включая таблицы.\n"
    "- Всегда возвращай разделы: 'Сильные стороны', 'Слабые стороны/Риски', 'Контекстуализация и сравнение' (с таблицей), 'Рекомендации'."
)

# Проверяем наличие API ключа
if not OPENROUTER_API_KEY:
    logger.warning("OPENROUTER_API_KEY не установлен. Установите переменную окружения для работы с API.")

def extract_text_from_pdf(file_path: str) -> str:
    """Извлекает текст из PDF файла."""
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        logger.info(f"Извлечен текст из {file_path}")
        return text
    except Exception as e:
        logger.error(f"Ошибка при извлечении текста из {file_path}: {e}")
        return ""

def get_file_hash(file_path: str) -> str:
    """Вычисляет SHA256 хэш файла."""
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        logger.error(f"Ошибка при вычислении хэша для {file_path}: {e}")
        return ""

def process_files_and_query(prompt: str, file_paths: list[str]):
    """Основная бизнес-логика: извлекает текст из файлов, проверяет дубликаты, отправляет запрос к модели."""
    logger.info("🎯 Начинаем обработку запроса")
    logger.info(f"💬 Промт пользователя: '{prompt[:100]}{'...' if len(prompt) > 100 else ''}'")
    logger.info(f"📁 Количество файлов: {len(file_paths)}")
    logger.info(f"📂 Пути к файлам: {file_paths}")
    
    combined_text = ""
    processed_hashes = set()

    # Обрабатываем файлы только если они есть
    if file_paths:
        logger.info("📄 Начинаем обработку файлов...")
        for i, file_path in enumerate(file_paths, 1):
            logger.info(f"📄 Обрабатываем файл {i}/{len(file_paths)}: {file_path}")
            
            if not os.path.isfile(file_path):
                logger.warning(f"⚠️ Файл не найден: {file_path}")
                continue

            file_hash = get_file_hash(file_path)
            logger.info(f"🔍 Хэш файла: {file_hash[:16]}...")
            
            if file_hash in processed_hashes:
                logger.info(f"🔄 Файл {file_path} является дубликатом, пропускаем.")
                continue

            processed_hashes.add(file_hash)

            # Поддержка только PDF для простоты примера
            if file_path.lower().endswith('.pdf'):
                logger.info(f"📖 Извлекаем текст из PDF: {file_path}")
                extracted_text = extract_text_from_pdf(file_path)
                if extracted_text.strip():
                    text_length = len(extracted_text)
                    logger.info(f"✅ Извлечено {text_length} символов из {file_path}")
                    combined_text += f"\n--- Содержимое файла {file_path} ---\n{extracted_text}\n"
                else:
                    logger.warning(f"⚠️ Не удалось извлечь текст из {file_path}")
            else:
                logger.warning(f"❌ Формат файла не поддерживается (пока только PDF): {file_path}")
        
        logger.info(f"📊 Общий размер извлеченного текста: {len(combined_text)} символов")
    else:
        logger.info("📄 Файлы не предоставлены")

    # Формирование сообщения для модели
    # Всегда добавляем системный промт философа-аналитика
    if combined_text.strip():
        logger.info("📝 Формируем сообщение с контекстом из файлов + системный промт")
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Контекст:\n{combined_text}\n\nВопрос: {prompt}"}
        ]
        logger.info(f"📊 Размер сообщения с контекстом: {len(messages[1]['content'])} символов")
    else:
        logger.info("📝 Файлы не предоставлены — используем только системный промт и вопрос пользователя")
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
        logger.info(f"📊 Размер сообщения без контекста: {len(messages[1]['content'])} символов")

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "google/gemma-3-27b-it:free", # Пример модели, можно изменить
        "messages": messages,
        "stream": False # Отключаем стриминг
    }

    # Проверяем наличие API ключа перед запросом
    if not OPENROUTER_API_KEY:
        return "Ошибка: API ключ OpenRouter не настроен. Установите переменную окружения OPENROUTER_API_KEY."

    try:
        logger.info("🚀 Отправляем запрос к OpenRouter API...")
        logger.info(f"📡 URL: {OPENROUTER_API_URL}")
        logger.info(f"🔑 API ключ: {'*' * 20}{OPENROUTER_API_KEY[-4:] if OPENROUTER_API_KEY else 'НЕ УСТАНОВЛЕН'}")
        logger.info(f"📝 Модель: {payload.get('model', 'НЕ УКАЗАНА')}")
        logger.info(f"💬 Количество сообщений: {len(payload.get('messages', []))}")
        logger.info(f"📊 Размер payload: {len(str(payload))} символов")
        logger.info(f"📋 Payload: {payload}")
        
        response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload)
        
        logger.info(f"📨 Получен ответ от API. Статус: {response.status_code}")
        logger.info(f"📋 Заголовки ответа: {dict(response.headers)}")
        
        response.raise_for_status()
        logger.info("✅ Запрос успешно обработан, парсим ответ...")

        # Логируем сырой ответ
        raw_content = response.text
        logger.info(f"📄 Сырой ответ от API: {raw_content[:500]}{'...' if len(raw_content) > 500 else ''}")
        logger.info(f"📊 Размер сырого ответа: {len(raw_content)} символов")
        
        if not raw_content.strip():
            logger.error("❌ Пустой ответ от API")
            return "API вернул пустой ответ."

        # Обработка обычного ответа (без стриминга)
        import json
        try:
            data = response.json()
            logger.info(f"📄 Получен JSON ответ размером: {len(str(data))} символов")
        except json.JSONDecodeError as e:
            logger.error(f"❌ Ошибка парсинга JSON: {e}")
            logger.error(f"📄 Сырой контент: {raw_content}")
            return f"Ошибка парсинга ответа от API: {e}"
        
        # Извлекаем ответ из JSON
        choices = data.get('choices', [])
        if choices:
            message = choices[0].get('message', {})
            content = message.get('content', '')
            if content:
                logger.info(f"📝 Получен ответ длиной: {len(content)} символов")
                return content
            else:
                logger.warning("⚠️ Пустой ответ от модели")
                return "Модель вернула пустой ответ."
        else:
            logger.warning("⚠️ Нет choices в ответе")
            return "Неожиданный формат ответа от API."

    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Ошибка запроса к OpenRouter API: {e}")
        logger.error(f"🔍 Тип ошибки: {type(e).__name__}")
        logger.error(f"📡 URL запроса: {OPENROUTER_API_URL}")
        return f"Ошибка при запросе к модели: {e}"
    except Exception as e:
        logger.error(f"💥 Неожиданная ошибка в бизнес-логике: {e}")
        logger.error(f"🔍 Тип ошибки: {type(e).__name__}")
        logger.error(f"📍 Стек вызовов: {str(e)}")
        return f"Произошла внутренняя ошибка: {e}"
