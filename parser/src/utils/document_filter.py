"""
Простая фильтрация документов по ключевым словам
"""
import re
import sys
import os
import logging
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.settings import EXCLUDE_KEYWORDS, INCLUDE_KEYWORDS

# Настройка логгера
logger = logging.getLogger(__name__)

def _normalize_keywords(keywords, default_keywords):
    """
    Нормализация ключевых слов: конвертация в список, удаление пробелов и пустых строк
    
    Args:
        keywords: Входные ключевые слова (строка, список или None)
        default_keywords: Ключевые слова по умолчанию
        
    Returns:
        list: Нормализованный список непустых строк
    """
    # Если keywords is None, используем default_keywords
    if keywords is None:
        keywords = default_keywords or []
    
    # Конвертируем строку в список
    if isinstance(keywords, str):
        keywords = [keywords]
    
    # Обрабатываем каждый элемент: конвертируем в строку, убираем пробелы, фильтруем пустые
    normalized = []
    for kw in keywords:
        if kw is not None:
            # Конвертируем в строку и убираем пробелы
            kw_str = str(kw).strip()
            if kw_str:  # Добавляем только непустые строки
                normalized.append(kw_str)
    
    return normalized

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
        # Нормализуем входные данные
        exclude_keywords = _normalize_keywords(exclude_keywords, EXCLUDE_KEYWORDS)
        include_keywords = _normalize_keywords(include_keywords, INCLUDE_KEYWORDS)
        
        # Безопасно компилируем паттерны для исключения
        self.exclude_patterns = self._compile_patterns_safely(exclude_keywords, exclude_is_regex, "exclude")
        
        # Безопасно компилируем паттерны для включения
        self.include_patterns = self._compile_patterns_safely(include_keywords, include_is_regex, "include")
    
    def _compile_patterns_safely(self, keywords, is_regex, pattern_type):
        """
        Безопасная компиляция регулярных выражений с обработкой ошибок
        
        Args:
            keywords: Список ключевых слов для компиляции
            is_regex: Если True, обрабатывать как regex, иначе экранировать
            pattern_type: Тип паттерна для логирования ("exclude" или "include")
            
        Returns:
            list: Список успешно скомпилированных regex объектов
        """
        patterns = []
        
        for keyword in keywords:
            # Проверяем что keyword является строкой и не пустой
            if not isinstance(keyword, str):
                logger.warning(f"Пропущен {pattern_type} паттерн '{keyword}': не является строкой.")
                continue
                
            # Убираем пробелы и проверяем что строка не пустая
            keyword = keyword.strip()
            if not keyword:
                logger.warning(f"Пропущен {pattern_type} паттерн: пустая строка или только пробелы.")
                continue
            
            try:
                if is_regex:
                    # Компилируем как regex
                    pattern = re.compile(keyword, re.IGNORECASE)
                else:
                    # Экранируем специальные символы и добавляем границы слов для точного совпадения
                    escaped_keyword = re.escape(keyword)
                    pattern = re.compile(rf'\b{escaped_keyword}\b', re.IGNORECASE)
                
                patterns.append(pattern)
                
            except re.error as e:
                # Логируем ошибку и пропускаем невалидный паттерн
                logger.warning(f"Не удалось скомпилировать {pattern_type} паттерн '{keyword}': {e}. Паттерн пропущен.")
                continue
        
        if not patterns:
            logger.warning(f"Не удалось скомпилировать ни одного {pattern_type} паттерна. Используется пустой список.")
        
        return patterns
    
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
