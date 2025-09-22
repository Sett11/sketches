#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import json

BASE = os.path.join(os.path.dirname(__file__), 'jsons')

def main():
    files = [f for f in os.listdir(BASE) if f.endswith('.json')]
    files.sort()
    print('file\tparts\tsections\tchapters\tarticles\tparagraphs')
    total_parts = total_sections = total_chapters = total_articles = total_paragraphs = 0
    for f in files:
        path = os.path.join(BASE, f)
        with open(path, 'r', encoding='utf-8') as fh:
            data = json.load(fh)
        parts = data.get('parts', [])
        sections = sum(len(p.get('sections', [])) for p in parts)
        chapters = sum(len(s.get('chapters', [])) for p in parts for s in p.get('sections', []))
        articles = sum(len(c.get('articles', [])) for p in parts for s in p.get('sections', []) for c in s.get('chapters', []))
        paragraphs = sum(len(a.get('paragraphs', [])) for p in parts for s in p.get('sections', []) for c in s.get('chapters', []) for a in c.get('articles', []))
        print(f"{f}\t{len(parts)}\t{sections}\t{chapters}\t{articles}\t{paragraphs}")
        total_parts += len(parts)
        total_sections += sections
        total_chapters += chapters
        total_articles += articles
        total_paragraphs += paragraphs
    print('\nTOTALS')
    print(total_parts, total_sections, total_chapters, total_articles, total_paragraphs)

if __name__ == '__main__':
    main()


