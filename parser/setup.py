#!/usr/bin/env python3
"""
Setup script for the Arbitrage Parser project
"""

import os
from setuptools import setup, find_packages

# Получаем директорию файла setup.py
setup_dir = os.path.dirname(os.path.abspath(__file__))

# Загружаем README.md с обработкой ошибок
try:
    with open(os.path.join(setup_dir, "README.md"), "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = ""

# Загружаем requirements.txt с обработкой ошибок
try:
    with open(os.path.join(setup_dir, "requirements.txt"), "r", encoding="utf-8") as fh:
        requirements = [line.strip() for line in fh if line.strip() and not line.lstrip().startswith("#")]
except FileNotFoundError:
    requirements = []

setup(
    name="arbitrage-parser",
    version="1.0.0",
    author="Arbitrage Parser Team",
    description="Парсер арбитражных дел для массовой загрузки решений судов",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    py_modules=["main"],  # main.py как top-level модуль
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Legal Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "arbitrage-parser=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "src": ["*.md", "*.txt", "*.yml", "*.yaml"],
    },
)
