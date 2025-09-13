"""
Простая фильтрация документов по ключевым словам
"""
import re
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.settings import EXCLUDE_KEYWORDS, INCLUDE_KEYWORDS

class DocumentFilter:
    """Простой фильтр документов"""
    
    def __init__(self, exclude_keywords=None, include_keywords=None, 
                 exclude_is_regex=False, include_is_regex=False):
        """
        Инициализация фильтра документов
        
        Args:
            exclude_keywords: Список ключевых слов для исключения (по умолчанию из настроек)
            include_keywords: Список ключевых слов для включения (по умолчанию из настроек)
            exclude_is_regex: Если True, exclude_keywords обрабатываются как regex (по умолчанию False)
            include_is_regex: Если True, include_keywords обрабатываются как regex (по умолчанию False)
        """
        # Используем переданные параметры или значения по умолчанию из настроек
        exclude_keywords = exclude_keywords if exclude_keywords is not None else EXCLUDE_KEYWORDS
        include_keywords = include_keywords if include_keywords is not None else INCLUDE_KEYWORDS
        
        # Компилируем паттерны для исключения
        if exclude_is_regex:
            self.exclude_patterns = [re.compile(keyword, re.IGNORECASE) for keyword in exclude_keywords]
        else:
            self.exclude_patterns = [re.compile(re.escape(keyword), re.IGNORECASE) for keyword in exclude_keywords]
        
        # Компилируем паттерны для включения
        if include_is_regex:
            self.include_patterns = [re.compile(keyword, re.IGNORECASE) for keyword in include_keywords]
        else:
            self.include_patterns = [re.compile(re.escape(keyword), re.IGNORECASE) for keyword in include_keywords]
    
    def should_exclude(self, text):
        """Проверить нужно ли исключить документ"""
        if not text:
            return False
            
        # Проверяем исключающие ключевые слова
        for pattern in self.exclude_patterns:
            if pattern.search(text):
                return True
        return False
    
    def should_include(self, text):
        """Проверить нужно ли включить документ"""
        if not text:
            return False
            
        # Проверяем включающие ключевые слова
        for pattern in self.include_patterns:
            if pattern.search(text):
                return True
        return False
    
    def filter_document(self, document_text, document_title=""):
        """Фильтровать документ по тексту и заголовку"""
        # Нормализуем None входы в пустые строки
        document_title = document_title if document_title is not None else ""
        document_text = document_text if document_text is not None else ""
        
        # Создаем полный текст без lower() - используем re.IGNORECASE
        full_text = f"{document_title} {document_text}"
        
        # Исключаем если есть исключающие слова
        if self.should_exclude(full_text):
            return False
        
        # Если список include_keywords пустой, возвращаем True (не исключаем все)
        if not self.include_patterns:
            return True
        
        # Включаем если есть включающие слова
        return self.should_include(full_text)
    
    def filter_documents_list(self, documents):
        """Фильтровать список документов"""
        filtered = []
        for doc in documents:
            # Проверяем разные возможные поля для текста документа
            doc_text = doc.get('Text', '') or doc.get('DocumentText', '') or doc.get('Content', '') or doc.get('Summary', '')
            doc_title = doc.get('Title', '') or doc.get('CaseTitle', '') or doc.get('Subject', '') or doc.get('Name', '')
            
            if self.filter_document(doc_text, doc_title):
                filtered.append(doc)
        return filtered

# Глобальный фильтр
document_filter = DocumentFilter()
