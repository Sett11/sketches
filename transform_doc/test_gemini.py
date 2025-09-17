#!/usr/bin/env python3
"""
Тест работы с OpenRouter API
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from word_processor import WordProcessor
from llm import OpenRouterClient

# Загружаем переменные окружения из .env файла
load_dotenv()

def test_openrouter():
    """Тестируем работу с OpenRouter API"""
    
    # Проверяем переменные окружения
    api_key = os.getenv('API_KEY')
    if not api_key:
        print("❌ API_KEY не найден в переменных окружения")
        print("💡 Установите переменную: set API_KEY=your_key_here")
        return
    
    print("✅ API_KEY найден")
    
    try:
        # Создаем клиент
        llm_client = OpenRouterClient()
        print("✅ OpenRouterClient создан успешно")
        
        # Создаем процессор
        processor = WordProcessor()
        print("✅ WordProcessor создан успешно")
        
        # Проверяем наличие файлов
        docs_files = [f for f in os.listdir("docs") if f.endswith(('.docx', '.doc'))]
        if not docs_files:
            print("❌ Нет файлов в папке docs/")
            return
        
        demo_file = docs_files[0]
        print(f"📄 Тестируем с файлом: {demo_file}")
        
        # Строим абсолютный путь к файлу
        demo_file_path = str(Path(__file__).parent / "docs" / demo_file)
        print(f"📁 Полный путь к файлу: {demo_file_path}")
        
        # Проверяем существование файла
        if not os.path.exists(demo_file_path):
            print(f"❌ Файл не найден: {demo_file_path}")
            return
        
        # Простой промт для теста
        prompt = "Измени все упоминания слова 'философия' на 'философствование' в тексте документа."
        
        # Обрабатываем документ
        result = processor.process_document(demo_file_path, prompt, llm_client)
        
        if result:
            print(f"✅ Документ обработан успешно: {result}")
        else:
            print("❌ Ошибка при обработке документа")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_openrouter()
