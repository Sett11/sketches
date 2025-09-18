#!/usr/bin/env python3
"""
Главный файл для обработки документов с помощью LLM
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from word_processor import WordProcessor
from llm import OpenRouterClient

# Загружаем переменные окружения из .env файла
load_dotenv()

def main():
    """Главная функция для интерактивной обработки документов"""
    
    print("🤖 Обработка документов с помощью LLM")
    print("=" * 50)
    
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
        print(f"✅ OpenRouterClient создан успешно (модель: {llm_client.model_name})")
        
        # Создаем процессор
        processor = WordProcessor()
        print("✅ WordProcessor создан успешно")
        
        # Проверяем наличие файлов в папке docs
        docs_files = [f for f in os.listdir("docs") if f.endswith(('.docx', '.doc'))]
        if not docs_files:
            print("❌ Нет файлов в папке docs/")
            print("💡 Поместите .docx или .doc файлы в папку docs/")
            return
        
        print(f"\n📁 Найдено файлов в docs/: {len(docs_files)}")
        for i, file in enumerate(docs_files, 1):
            print(f"  {i}. {file}")
        
        # Выбор файла
        while True:
            try:
                choice = input(f"\n📄 Выберите файл (1-{len(docs_files)}) или введите имя файла: ").strip()
                
                # Если введен номер
                if choice.isdigit():
                    file_index = int(choice) - 1
                    if 0 <= file_index < len(docs_files):
                        selected_file = docs_files[file_index]
                        break
                    else:
                        print(f"❌ Введите число от 1 до {len(docs_files)}")
                        continue
                
                # Если введено имя файла
                if choice in docs_files:
                    selected_file = choice
                    break
                else:
                    print(f"❌ Файл '{choice}' не найден в папке docs/")
                    print("💡 Доступные файлы:", ", ".join(docs_files))
                    continue
                    
            except KeyboardInterrupt:
                print("\n👋 Выход...")
                return
            except Exception as e:
                print(f"❌ Ошибка ввода: {e}")
                continue
        
        print(f"✅ Выбран файл: {selected_file}")
        
        # Ввод промта
        print("\n📝 Введите промт для обработки документа:")
        while True:
            try:
                prompt = input("\n🔤 Ваш промт: ").strip()
                if prompt:
                    break
                else:
                    print("❌ Промт не может быть пустым")
                    continue
            except KeyboardInterrupt:
                print("\n👋 Выход...")
                return
            except Exception as e:
                print(f"❌ Ошибка ввода: {e}")
                continue
        
        print(f"✅ Промт принят: {prompt}")
        
        # Обработка документа
        print(f"\n🔄 Обрабатываем документ: {selected_file}")
        print("⏳ Это может занять некоторое время...")
        
        result = processor.process_document(selected_file, prompt, llm_client)
        
        if result:
            print(f"\n✅ Документ обработан успешно!")
            print(f"📁 Результат сохранен: {result}")
            print(f"💾 Исходный файл: docs/{selected_file}")
            print(f"📄 Обработанный файл: {result}")
        else:
            print("❌ Ошибка при обработке документа")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
