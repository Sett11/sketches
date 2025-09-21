#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Парсер DOCX файлов
"""

import json
import os
import re
from typing import Dict, List, Any, Optional
from docx import Document
from mylogger import Logger


class Parser:
    """Парсер DOCX файлов"""
    
    def __init__(self):
        # Инициализация логгера
        self.logger = Logger('Parser', 'logs/parser.log')
        self.logger.info("Инициализация DOCX парсера")

    def read_docx_file(self, file_path: str) -> Document:
        """Чтение DOCX файла"""
        self.logger.debug(f"Чтение DOCX файла: {file_path}")
        try:
            doc = Document(file_path)
            self.logger.info(f"DOCX файл успешно прочитан: {file_path}")
            return doc
        except Exception as e:
            self.logger.error(f"Ошибка чтения DOCX файла {file_path}: {str(e)}")
            raise

    def clean_title(self, title: str) -> str:
        """Очистка названия от лишних символов"""
        # Убираем точки в начале и конце
        title = title.strip(' .')
        # Убираем лишние пробелы
        title = re.sub(r'\s+', ' ', title)
        return title

    def extract_structure(self, doc: Document) -> Dict[str, Any]:
        """Извлечение структуры документа из DOCX"""
        self.logger.debug("Начало извлечения структуры из DOCX")
        
        structure = {
            'document': '',
            'parts': []
        }
        
        # Текущие элементы на каждом уровне
        current_elements = {
            'part': None,
            'section': None,
            'chapter': None,
            'article': None,
        }
        
        parts_found = 0
        sections_found = 0
        chapters_found = 0
        articles_found = 0
        paragraphs_found = 0
        
        # Обрабатываем каждый параграф
        for i, paragraph in enumerate(doc.paragraphs):
            text = paragraph.text.strip()
            if not text:
                continue
            
            self.logger.debug(f"Обрабатываю параграф {i+1}: {text[:100]}...")
            
            # Поиск частей (ищем явные заголовки "ЧАСТЬ")
            if re.match(r'^ЧАСТЬ\s+([IVX]+|[А-ЯЁ]+|[0-9]+)', text, re.IGNORECASE):
                parts_found += 1
                self.logger.info(f"Найдена часть в параграфе {i+1}: {text}")
                
                # Сохраняем предыдущую часть, если есть
                if current_elements['part']:
                    structure['parts'].append(current_elements['part'])
                
                # Извлекаем номер части
                part_number = self.extract_number_after_keyword(text, 'ЧАСТЬ')
                part_title = text.replace(f'ЧАСТЬ {part_number}', '').strip()
                current_elements['part'] = {
                    'number': part_number,
                    'title': self.clean_title(part_title),
                    'sections': []
                }
                # Сбрасываем подуровни
                current_elements['section'] = None
                current_elements['chapter'] = None
                current_elements['article'] = None
            
            # Поиск разделов
            elif re.match(r'^Раздел\s+([IVX]+|[А-ЯЁ]+|[0-9]+)', text, re.IGNORECASE):
                sections_found += 1
                self.logger.info(f"Найден раздел в параграфе {i+1}: {text}")
                
                # Сохраняем предыдущий раздел, если есть
                if current_elements['section'] and current_elements['part']:
                    current_elements['part']['sections'].append(current_elements['section'])
                
                # Извлекаем номер раздела
                section_number = self.extract_number_after_keyword(text, 'РАЗДЕЛ')
                section_title = text.replace(f'Раздел {section_number}', '').strip()
                current_elements['section'] = {
                    'number': section_number,
                    'title': self.clean_title(section_title),
                    'chapters': []
                }
                # Сбрасываем подуровни
                current_elements['chapter'] = None
                current_elements['article'] = None
            
            # Поиск глав
            elif re.match(r'^Глава\s+([0-9]+)', text, re.IGNORECASE):
                chapters_found += 1
                self.logger.info(f"Найдена глава в параграфе {i+1}: {text}")
                
                # Сохраняем предыдущую главу, если есть
                if current_elements['chapter'] and current_elements['section']:
                    current_elements['section']['chapters'].append(current_elements['chapter'])
                
                # Извлекаем номер главы
                chapter_number = self.extract_number_after_keyword(text, 'ГЛАВА')
                chapter_title = text.replace(f'Глава {chapter_number}', '').strip()
                current_elements['chapter'] = {
                    'number': int(chapter_number) if chapter_number.isdigit() else 0,
                    'title': self.clean_title(chapter_title),
                    'articles': []
                }
                # Сбрасываем подуровни
                current_elements['article'] = None
            
            # Поиск статей
            elif re.match(r'^Статья\s+([0-9]+)', text, re.IGNORECASE):
                articles_found += 1
                self.logger.info(f"Найдена статья в параграфе {i+1}: {text}")
                
                # Сохраняем предыдущую статью, если есть
                if current_elements['article'] and current_elements['chapter']:
                    current_elements['chapter']['articles'].append(current_elements['article'])
                
                # Извлекаем номер статьи
                article_number = self.extract_number_after_keyword(text, 'СТАТЬЯ')
                article_title = text.replace(f'Статья {article_number}', '').strip()
                current_elements['article'] = {
                    'number': int(article_number) if article_number.isdigit() else 0,
                    'title': self.clean_title(article_title),
                    'paragraphs': []
                }
            
            # Поиск пунктов (включая подпункты)
            elif current_elements['article'] and self.is_paragraph(text):
                paragraphs_found += 1
                self.logger.info(f"Найден пункт в параграфе {i+1}: {text}")
                
                # Извлекаем структуру пункта
                paragraph_data = self.extract_paragraph_structure(text)
                if paragraph_data:
                    current_elements['article']['paragraphs'].append(paragraph_data)
        
        # Сохраняем последние элементы
        if current_elements['article'] and current_elements['chapter']:
            current_elements['chapter']['articles'].append(current_elements['article'])
        if current_elements['chapter'] and current_elements['section']:
            current_elements['section']['chapters'].append(current_elements['chapter'])
        if current_elements['section'] and current_elements['part']:
            current_elements['part']['sections'].append(current_elements['section'])
        if current_elements['part']:
            structure['parts'].append(current_elements['part'])
        
        # Если нет частей, но есть разделы, создаем общую часть
        if not structure['parts'] and sections_found > 0:
            self.logger.info("Части не найдены, но есть разделы. Создаю общую часть.")
            
            # Создаем основную часть
            main_part = {
                'number': '1',
                'title': 'Основная часть',
                'sections': []
            }
            
            # Пересобираем структуру без частей
            current_section = None
            current_chapter = None
            current_article = None
            
            for i, paragraph in enumerate(doc.paragraphs):
                text = paragraph.text.strip()
                if not text:
                    continue
                
                # Поиск разделов
                if re.match(r'^Раздел\s+([IVX]+|[А-ЯЁ]+|[0-9]+)', text, re.IGNORECASE):
                    # Сохраняем предыдущий раздел
                    if current_section:
                        main_part['sections'].append(current_section)
                    
                    section_number = self.extract_number_after_keyword(text, 'РАЗДЕЛ')
                    section_title = text.replace(f'Раздел {section_number}', '').strip()
                    current_section = {
                        'number': section_number,
                        'title': self.clean_title(section_title),
                        'chapters': []
                    }
                    current_chapter = None
                    current_article = None
                
                # Поиск глав
                elif re.match(r'^Глава\s+([0-9]+)', text, re.IGNORECASE):
                    # Сохраняем предыдущую главу
                    if current_chapter and current_section:
                        current_section['chapters'].append(current_chapter)
                    
                    chapter_number = self.extract_number_after_keyword(text, 'ГЛАВА')
                    chapter_title = text.replace(f'Глава {chapter_number}', '').strip()
                    current_chapter = {
                        'number': int(chapter_number) if chapter_number.isdigit() else 0,
                        'title': self.clean_title(chapter_title),
                        'articles': []
                    }
                    current_article = None
                
                # Поиск статей
                elif re.match(r'^Статья\s+([0-9]+)', text, re.IGNORECASE):
                    # Сохраняем предыдущую статью
                    if current_article and current_chapter:
                        current_chapter['articles'].append(current_article)
                    
                    article_number = self.extract_number_after_keyword(text, 'СТАТЬЯ')
                    article_title = text.replace(f'Статья {article_number}', '').strip()
                    current_article = {
                        'number': int(article_number) if article_number.isdigit() else 0,
                        'title': self.clean_title(article_title),
                        'paragraphs': []
                    }
                
                # Поиск пунктов (включая подпункты)
                elif current_article and self.is_paragraph(text):
                    paragraph_data = self.extract_paragraph_structure(text)
                    if paragraph_data:
                        current_article['paragraphs'].append(paragraph_data)
            
            # Сохраняем последние элементы
            if current_article and current_chapter:
                current_chapter['articles'].append(current_article)
            if current_chapter and current_section:
                current_section['chapters'].append(current_chapter)
            if current_section:
                main_part['sections'].append(current_section)
            
            structure['parts'].append(main_part)
        
        # Итоговое логирование
        parts_count = len(structure['parts'])
        self.logger.info(f"Извлечение структуры завершено. Создано частей: {parts_count}")
        
        return structure

    def is_paragraph(self, text: str) -> bool:
        """Проверка, является ли текст пунктом или подпунктом"""
        # Ищем паттерны: 1., 1.1., 1.2., 2., 2.1., 2.2. и т.д.
        patterns = [
            r'^(\d+)\.\s',  # 1., 2., 3.
            r'^(\d+)\.(\d+)\.\s',  # 1.1., 1.2., 2.1.
            r'^(\d+)\)\s',  # 1), 2), 3)
            r'^(\d+)\.(\d+)\)\s',  # 1.1), 1.2), 2.1)
        ]
        
        for pattern in patterns:
            if re.match(pattern, text):
                return True
        return False

    def extract_paragraph_structure(self, text: str) -> Dict[str, Any]:
        """Извлечение структуры пункта (включая подпункты)"""
        # Ищем основной пункт (1., 2., 3.)
        main_match = re.match(r'^(\d+)\.\s*(.+)', text)
        if main_match:
            paragraph_number = main_match.group(1) + '.'
            paragraph_text = main_match.group(2).strip()
            
            return {
                'number': paragraph_number,
                'text': paragraph_text,
                'subparagraphs': []
            }
        
        # Ищем подпункт (1.1., 1.2., 2.1.)
        sub_match = re.match(r'^(\d+)\.(\d+)\.\s*(.+)', text)
        if sub_match:
            sub_number = sub_match.group(1) + '.' + sub_match.group(2) + '.'
            sub_text = sub_match.group(3).strip()
            
            return {
                'number': sub_number,
                'text': sub_text,
                'subparagraphs': []
            }
        
        # Ищем пункт со скобками (1), 2), 3))
        bracket_match = re.match(r'^(\d+)\)\s*(.+)', text)
        if bracket_match:
            bracket_number = bracket_match.group(1) + ')'
            bracket_text = bracket_match.group(2).strip()
            
            return {
                'number': bracket_number,
                'text': bracket_text,
                'subparagraphs': []
            }
        
        # Ищем подпункт со скобками (1.1), 1.2), 2.1))
        bracket_sub_match = re.match(r'^(\d+)\.(\d+)\)\s*(.+)', text)
        if bracket_sub_match:
            bracket_sub_number = bracket_sub_match.group(1) + '.' + bracket_sub_match.group(2) + ')'
            bracket_sub_text = bracket_sub_match.group(3).strip()
            
            return {
                'number': bracket_sub_number,
                'text': bracket_sub_text,
                'subparagraphs': []
            }
        
        return None

    def extract_number_after_keyword(self, text: str, keyword: str) -> str:
        """Извлечение номера после ключевого слова"""
        pattern = rf'{keyword}\s+([IVX]+|[А-ЯЁ]+|[0-9]+)'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
        return ""

    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """Парсинг одного DOCX файла"""
        self.logger.info(f"Начало обработки файла: {file_path}")
        try:
            # Читаем файл
            doc = self.read_docx_file(file_path)
            self.logger.debug(f"DOCX файл прочитан, количество параграфов: {len(doc.paragraphs)}")
            
            # Извлекаем структуру
            structure = self.extract_structure(doc)
            
            # Устанавливаем название документа из имени файла
            file_name = os.path.basename(file_path)
            structure['document'] = file_name.replace('.docx', '')
            
            self.logger.info(f"Файл {file_name} успешно обработан")
            return structure
            
        except Exception as e:
            self.logger.error(f"Ошибка при обработке файла {file_path}: {str(e)}")
            return {
                'document': os.path.basename(file_path).replace('.docx', ''),
                'error': f'Ошибка обработки файла: {str(e)}',
                'parts': []
            }

    def process_all_files(self, input_dir: str, output_dir: str):
        """Обработка всех DOCX файлов в директории"""
        self.logger.info(f"Начало обработки всех файлов из {input_dir} в {output_dir}")
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            self.logger.info(f"Создана директория {output_dir}")
        
        docx_files = [f for f in os.listdir(input_dir) if f.endswith('.docx')]
        self.logger.info(f"Найдено {len(docx_files)} DOCX файлов для обработки")
        
        for i, docx_file in enumerate(docx_files, 1):
            self.logger.info(f"Обрабатываю файл {i}/{len(docx_files)}: {docx_file}")
            print(f"Обрабатываю файл {i}/{len(docx_files)}: {docx_file}")
            
            input_path = os.path.join(input_dir, docx_file)
            output_path = os.path.join(output_dir, docx_file.replace('.docx', '.json'))
            
            # Парсим файл
            structure = self.parse_file(input_path)
            
            # Логируем результат парсинга
            parts_count = len(structure.get('parts', []))
            if 'error' in structure:
                self.logger.error(f"Ошибка при обработке {docx_file}: {structure['error']}")
            else:
                self.logger.info(f"Файл {docx_file} обработан успешно. Найдено частей: {parts_count}")
            
            # Сохраняем JSON
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(structure, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"Сохранен: {output_path}")
            print(f"Сохранен: {output_path}")
        
        self.logger.info("Обработка всех файлов завершена")


def main():
    """Основная функция"""
    parser = Parser()
    parser.process_all_files('docs', 'jsons')


if __name__ == "__main__":
    main()
