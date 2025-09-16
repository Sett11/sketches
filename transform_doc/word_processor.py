#!/usr/bin/env python3
"""
Простой процессор Word документов на python-docx
Тестирует сохранение форматирования при изменении содержимого
"""

import os
import traceback
from datetime import datetime
from typing import Dict, List

from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

class WordProcessor:
    """Простой процессор Word документов с сохранением форматирования"""
    
    def __init__(self):
        self.document = None
    
    def load_document(self, filepath: str) -> 'WordProcessor':
        """Загружает документ из файла"""
        print(f"📖 Загружаем документ: {filepath}")
        self.document = Document(filepath)
        print("✅ Документ загружен успешно")
        return self
    
    def process_document(self, input_filepath: str, changes: Dict[str, str], output_filename: str = None) -> str:
        """
        Обрабатывает документ: читает, применяет изменения и сохраняет в new_docs
        
        Args:
            input_filepath: Путь к исходному файлу (относительно docs/)
            changes: Словарь замен {старый_текст: новый_текст}
            output_filename: Имя выходного файла (если не указано, генерируется автоматически)
        
        Returns:
            Путь к обработанному файлу
        """
        # Формируем полный путь к исходному файлу
        if not input_filepath.startswith('docs/'):
            input_filepath = f"docs/{input_filepath}"
        
        if not os.path.exists(input_filepath):
            raise FileNotFoundError(f"Файл не найден: {input_filepath}")
        
        print(f"📖 Обрабатываем документ: {input_filepath}")
        
        # Загружаем документ
        self.load_document(input_filepath)
        
        # Применяем изменения
        self.apply_changes(changes)
        
        # Генерируем имя выходного файла
        if not output_filename:
            base_name = os.path.splitext(os.path.basename(input_filepath))[0]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"{base_name}_processed_{timestamp}.docx"
        
        # Убеждаемся, что папка new_docs существует
        os.makedirs("new_docs", exist_ok=True)
        output_path = f"new_docs/{output_filename}"
        
        # Сохраняем обработанный документ
        self.save_document(output_path)
        
        print(f"✅ Обработка завершена: {output_path}")
        return output_path
    
    def apply_changes(self, changes: Dict[str, str]) -> 'WordProcessor':
        """Применяет изменения к документу с сохранением форматирования"""
        if not self.document:
            raise ValueError("Документ не загружен!")
        
        print("🔧 Применяем изменения...")
        changes_made = 0
        
        # Изменяем параграфы
        for paragraph in self.document.paragraphs:
            if paragraph.text.strip():
                original_text = paragraph.text
                new_text = original_text
                
                # Применяем замены
                for old_text, new_text_replacement in changes.items():
                    if old_text in new_text:
                        new_text = new_text.replace(old_text, new_text_replacement)
                        print(f"  🔄 Заменяем: '{old_text}' -> '{new_text_replacement}'")
                        changes_made += 1
                
                # Обновляем текст с сохранением форматирования
                if new_text != original_text:
                    self._update_paragraph_text(paragraph, new_text)
        
        # Изменяем таблицы
        for table in self.document.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        if paragraph.text.strip():
                            original_text = paragraph.text
                            new_text = original_text
                            
                            # Применяем замены
                            for old_text, new_text_replacement in changes.items():
                                if old_text in new_text:
                                    new_text = new_text.replace(old_text, new_text_replacement)
                                    print(f"  🔄 В таблице заменяем: '{old_text}' -> '{new_text_replacement}'")
                                    changes_made += 1
                            
                            # Обновляем текст
                            if new_text != original_text:
                                self._update_paragraph_text(paragraph, new_text)
        
        print(f"✅ Изменения применены: {changes_made} замен")
        return self
    
    def _update_paragraph_text(self, paragraph, new_text: str):
        """Обновляет текст параграфа с сохранением форматирования"""
        if paragraph.runs:
            # Сохраняем форматирование первого run
            first_run = paragraph.runs[0]
            first_run.text = new_text
            
            # Очищаем остальные runs
            for run in paragraph.runs[1:]:
                run.text = ''
        else:
            # Если нет runs, просто заменяем текст
            paragraph.text = new_text
    
    def save_document(self, output_path: str) -> 'WordProcessor':
        """Сохраняет документ"""
        if not self.document:
            raise ValueError("Документ не загружен!")
        
        print(f"💾 Сохраняем документ: {output_path}")
        self.document.save(output_path)
        print("✅ Документ сохранен успешно")
        return self
    
    def show_document_info(self):
        """Показывает информацию о документе"""
        if not self.document:
            raise ValueError("Документ не загружен!")
        
        print("\n📋 Информация о документе:")
        print("-" * 40)
        
        # Подсчитываем элементы
        paragraphs = [p for p in self.document.paragraphs if p.text.strip()]
        tables = self.document.tables
        
        print(f"Параграфов: {len(paragraphs)}")
        print(f"Таблиц: {len(tables)}")
        
        # Показываем форматирование
        print("\n🎨 Форматирование:")
        for i, paragraph in enumerate(paragraphs[:5]):  # Показываем первые 5
            print(f"\nПараграф {i+1}:")
            print(f"  Текст: {paragraph.text[:50]}...")
            print(f"  Выравнивание: {paragraph.alignment}")
            
            if paragraph.runs:
                print("  Форматирование:")
                for j, run in enumerate(paragraph.runs):
                    if run.text.strip():
                        print(f"    Run {j+1}: жирный={run.bold}, курсив={run.italic}")

def main():
    """Демонстрация работы процессора с реальными файлами"""
    print("🔧 ПРОЦЕССОР WORD ДОКУМЕНТОВ")
    print("=" * 50)
    
    # Создаем процессор
    processor = WordProcessor()
    
    try:
        # Проверяем наличие файлов в папке docs
        docs_files = [f for f in os.listdir("docs") if f.endswith(('.docx', '.doc'))]
        
        if not docs_files:
            print("📁 Папка docs пуста. Поместите .docx файлы в папку docs/ для обработки.")
            print("💡 Пример использования:")
            print("   processor = WordProcessor()")
            print("   changes = {'старый текст': 'новый текст'}")
            print("   result = processor.process_document('мой_файл.docx', changes)")
            return
        
        # Берем первый найденный файл для демонстрации
        demo_file = docs_files[0]
        print(f"📄 Найден файл для демонстрации: {demo_file}")
        
        # Определяем изменения (имитация LLM)
        changes = {
            'ООО "ТЕСТОВАЯ КОМПАНИЯ"': 'ООО "НОВАЯ КОМПАНИЯ"',
            'ИП ИВАНОВ ИВАН ИВАНОВИЧ': 'ИП ПЕТРОВ ПЕТР ПЕТРОВИЧ',
            '1234567890': '1111111111',
            '0987654321': '2222222222',
            '100 000': '150 000',
            '25 000': '30 000',
            '175 000': '200 000',
            'сто семьдесят пять тысяч': 'двести тысяч'
        }
        
        # Обрабатываем документ
        result_file = processor.process_document(demo_file, changes)
        
        print("\n🎉 ОБРАБОТКА ЗАВЕРШЕНА!")
        print("✅ Файлы:")
        print(f"   - Исходный: docs/{demo_file}")
        print(f"   - Обработанный: {result_file}")
        print("✅ Форматирование сохранено!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
