use crate::swc_parser::SwcParser;
use anyhow::Result;
use dc_core::call_graph::{CallGraph, CallGraphBuilder};
use std::path::PathBuf;

/// Построитель графа вызовов для TypeScript проекта
pub struct TypeScriptCallGraphBuilder {
    core_builder: CallGraphBuilder,
    src_paths: Vec<PathBuf>,
    parser: SwcParser,
}

impl TypeScriptCallGraphBuilder {
    /// Создает новый построитель
    pub fn new(src_paths: Vec<PathBuf>) -> Self {
        Self {
            core_builder: CallGraphBuilder::new(),
            src_paths,
            parser: SwcParser::new(),
        }
    }

    /// Строит граф для TypeScript проекта
    pub fn build_graph(&mut self) -> Result<CallGraph> {
        // 1. Находим все .ts/.tsx файлы в src_paths
        let mut files = Vec::new();
        for src_path in &self.src_paths {
            self.find_ts_files(src_path, &mut files)?;
        }

        // 2. Для каждого файла парсим и обрабатываем
        // TODO: Полная реализация будет на Этапе 5 (извлечение схем)
        // Пока создаем минимальный граф с модулями
        for file in files {
            // Парсим через swc
            let _module = self.parser.parse_file(&file)?;

            // TODO: Реализовать полное построение графа:
            // - Извлечение импортов
            // - Извлечение вызовов функций
            // - Извлечение Zod схем
            // - Построение графа: components → services → API calls
            // - Связывание через axios/fetch вызовы
        }

        // Возвращаем граф (пока может быть пустым, если TypeScriptParser не реализован)
        Ok(self.core_builder.into_graph())
    }

    fn find_ts_files(&self, dir: &PathBuf, files: &mut Vec<PathBuf>) -> Result<()> {
        if dir.is_file() {
            if let Some(ext) = dir.extension() {
                if ext == "ts" || ext == "tsx" {
                    files.push(dir.clone());
                }
            }
            return Ok(());
        }

        if dir.is_dir() {
            for entry in std::fs::read_dir(dir)? {
                let entry = entry?;
                let path = entry.path();
                self.find_ts_files(&path, files)?;
            }
        }

        Ok(())
    }
}
