#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Сводный анализ чанков для эмбеддингов
"""

import os
import json
from pathlib import Path

def analyze_embedding_chunks():
    """Анализирует созданные чанки для эмбеддингов"""
    
    jsons_dir = "jsons_2"
    if not os.path.exists(jsons_dir):
        print(f"❌ Папка {jsons_dir} не найдена")
        return
    
    files = list(Path(jsons_dir).glob("*.json"))
    if not files:
        print(f"❌ JSON файлы не найдены в папке {jsons_dir}")
        return
    
    print(f"📊 Анализ чанков для эмбеддингов")
    print(f"📁 Найдено файлов: {len(files)}")
    print("=" * 60)
    
    total_chunks = 0
    total_articles = 0
    
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            source_file = data.get('source_file', 'Unknown')
            articles_count = data.get('total_articles', 0)
            chunks = data.get('chunks', [])
            chunks_count = len(chunks)
            
            total_articles += articles_count
            total_chunks += chunks_count
            
            print(f"📄 {source_file}")
            print(f"   Статей: {articles_count}")
            print(f"   Чанков: {chunks_count}")
            
            # Показываем примеры чанков
            if chunks:
                print(f"   Примеры чанков:")
                for i, chunk in enumerate(chunks[:3]):  # Показываем первые 3 чанка
                    article_num = chunk.get('article_number', '?')
                    chunk_text = chunk.get('text', '')[:100] + '...' if len(chunk.get('text', '')) > 100 else chunk.get('text', '')
                    print(f"     {i+1}. Статья {article_num}: {chunk_text}")
            
            print()
            
        except Exception as e:
            print(f"❌ Ошибка при чтении файла {file_path}: {e}")
    
    print("=" * 60)
    print(f"📈 ИТОГО:")
    print(f"   Всего статей: {total_articles}")
    print(f"   Всего чанков: {total_chunks}")
    print(f"   Среднее чанков на статью: {total_chunks/total_articles:.1f}" if total_articles > 0 else "   Среднее чанков на статью: 0")

if __name__ == "__main__":
    analyze_embedding_chunks()
