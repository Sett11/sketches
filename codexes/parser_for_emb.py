#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Парсер для создания чанков для эмбеддингов
Разбивает документы по статьям (big_chunk) и далее по 750 символов (small_chunk)
"""

import os
import re
import json
import logging
from pathlib import Path

# Для работы с .docx файлами
try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    print("⚠️ Библиотека python-docx не установлена. Установите: pip install python-docx")

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/embedding_parser.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def read_docx_file(file_path):
    """Читает .docx файл и возвращает текст"""
    if not DOCX_AVAILABLE:
        logger.error("Библиотека python-docx не установлена")
        return None
    
    try:
        doc = Document(file_path)
        text = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text.append(paragraph.text.strip())
        return '\n'.join(text)
    except Exception as e:
        logger.error(f"Ошибка чтения .docx файла {file_path}: {e}")
        return None

def clean_text(text):
    """Очистка текста от лишних символов и нормализация"""
    # Убираем множественные пробелы и переносы
    text = re.sub(r'\s+', ' ', text)
    # Убираем лишние символы в начале и конце
    text = text.strip()
    return text

def split_by_articles(text):
    """
    Разбивает текст по статьям закона
    Ищет паттерны: "Статья 1", "Статья 2", "Статья 10" и т.д.
    Возвращает список словарей с номером статьи и текстом
    """
    # Паттерн для поиска статей: "Статья" + цифра(ы) (с возможными пробелами)
    article_pattern = r'(?=Статья\s*\d+)'
    
    # Разбиваем текст по статьям
    article_parts = re.split(article_pattern, text)
    
    articles = []
    for part in article_parts:
        part = clean_text(part)
        if not part:
            continue
            
        # Ищем номер статьи в начале части
        article_match = re.match(r'^Статья\s*(\d+)\s*(.*)', part)
        if article_match:
            article_number = article_match.group(1)
            article_text = article_match.group(2).strip()
            
            # Если текст начинается с заголовка статьи, извлекаем его
            if article_text:
                articles.append({
                    'number': article_number,
                    'text': article_text,
                    'title': article_text.split('\n')[0] if '\n' in article_text else article_text[:100] + '...'
                })
    
    logger.info(f"Найдено статей: {len(articles)}")
    return articles

def split_into_chunks(text, chunk_size=750):
    """
    Разбивает текст на чанки заданного размера
    Старается разбивать по предложениям, чтобы не резать по словам
    """
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    current_pos = 0
    
    while current_pos < len(text):
        # Определяем конец текущего чанка
        end_pos = current_pos + chunk_size
        
        if end_pos >= len(text):
            # Последний чанк
            chunks.append(text[current_pos:])
            break
        
        # Ищем ближайший конец предложения в пределах чанка
        chunk_text = text[current_pos:end_pos]
        
        # Ищем последние знаки препинания
        last_sentence_end = max(
            chunk_text.rfind('.'),
            chunk_text.rfind('!'),
            chunk_text.rfind('?'),
            chunk_text.rfind(';')
        )
        
        if last_sentence_end > chunk_size * 0.5:  # Если нашли подходящий разрыв
            actual_end = current_pos + last_sentence_end + 1
        else:
            # Если не нашли подходящий разрыв, ищем последний пробел
            last_space = chunk_text.rfind(' ')
            if last_space > chunk_size * 0.7:
                actual_end = current_pos + last_space
            else:
                actual_end = end_pos
        
        chunk = text[current_pos:actual_end].strip()
        if chunk:
            chunks.append(chunk)
        
        current_pos = actual_end
    
    return chunks

def process_document(file_path, output_dir):
    """Обрабатывает один документ и создает JSON с чанками"""
    logger.info(f"Обрабатываем файл: {file_path}")
    
    try:
        # Читаем файл в зависимости от расширения
        if file_path.endswith('.docx'):
            content = read_docx_file(file_path)
            if not content:
                logger.error(f"Не удалось прочитать .docx файл {file_path}")
                return None
        else:
            # Для .txt и .rtf файлов
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        
        # Разбиваем по статьям
        articles = split_by_articles(content)
        
        if not articles:
            logger.warning(f"В файле {file_path} не найдено статей")
            return None
        
        # Обрабатываем каждую статью
        result = {
            "source_file": os.path.basename(file_path),
            "total_articles": len(articles),
            "chunks": []
        }
        
        chunk_id = 0
        for article_idx, article in enumerate(articles):
            logger.info(f"Обрабатываем статью {article['number']} ({article_idx + 1}/{len(articles)})")
            
            # Разбиваем статью на чанки
            chunks = split_into_chunks(article['text'], chunk_size=750)
            
            for chunk_idx, chunk in enumerate(chunks):
                chunk_data = {
                    "id": chunk_id,
                    "article_number": article['number'],
                    "article_title": article['title'],
                    "article_index": article_idx + 1,
                    "chunk_index": chunk_idx + 1,
                    "total_chunks_in_article": len(chunks),
                    "text": chunk,
                    "text_length": len(chunk),
                    "source_info": f"Статья {article['number']} из {os.path.basename(file_path)}"
                }
                result["chunks"].append(chunk_data)
                chunk_id += 1
        
        # Сохраняем результат
        output_file = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(file_path))[0]}_chunks.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Создан файл: {output_file}")
        logger.info(f"Всего чанков: {len(result['chunks'])}")
        
        return result
        
    except Exception as e:
        logger.error(f"Ошибка при обработке файла {file_path}: {e}")
        return None

def main():
    """Основная функция"""
    # Создаем папки
    docs_dir = "docs"
    output_dir = "jsons_2"
    logs_dir = "logs"
    
    for dir_path in [output_dir, logs_dir]:
        os.makedirs(dir_path, exist_ok=True)
    
    # Получаем список файлов
    if not os.path.exists(docs_dir):
        logger.error(f"Папка {docs_dir} не найдена")
        return
    
    files = [f for f in os.listdir(docs_dir) if f.endswith(('.rtf', '.txt', '.docx'))]
    
    if not files:
        logger.warning(f"В папке {docs_dir} не найдено файлов для обработки")
        return
    
    logger.info(f"Найдено файлов для обработки: {len(files)}")
    
    # Обрабатываем каждый файл
    total_chunks = 0
    processed_files = 0
    
    for file_name in files:
        file_path = os.path.join(docs_dir, file_name)
        result = process_document(file_path, output_dir)
        
        if result:
            total_chunks += len(result["chunks"])
            processed_files += 1
    
    logger.info(f"Обработка завершена!")
    logger.info(f"Обработано файлов: {processed_files}")
    logger.info(f"Всего чанков создано: {total_chunks}")

if __name__ == "__main__":
    main()
