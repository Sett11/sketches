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
    
    def __init__(self):
        self.exclude_patterns = [re.compile(keyword, re.IGNORECASE) for keyword in EXCLUDE_KEYWORDS]
        self.include_patterns = [re.compile(keyword, re.IGNORECASE) for keyword in INCLUDE_KEYWORDS]
    
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
        full_text = f"{document_title} {document_text}".lower()
        
        # Исключаем если есть исключающие слова
        if self.should_exclude(full_text):
            return False
        
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
