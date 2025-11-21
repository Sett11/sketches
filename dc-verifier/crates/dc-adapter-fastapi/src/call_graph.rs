use crate::extractor::FastApiExtractor;
use anyhow::Result;
use dc_core::call_graph::{CallGraph, CallGraphBuilder};
use std::path::PathBuf;

/// Построитель графа вызовов для FastAPI приложения
pub struct FastApiCallGraphBuilder {
    core_builder: CallGraphBuilder,
    app_path: PathBuf,
}

impl FastApiCallGraphBuilder {
    /// Создает новый построитель
    pub fn new(app_path: PathBuf) -> Self {
        Self {
            core_builder: CallGraphBuilder::new(),
            app_path,
        }
    }

    /// Строит граф для FastAPI приложения
    pub fn build_graph(&mut self) -> Result<CallGraph> {
        // Определяем корень проекта
        let project_root = self
            .app_path
            .parent()
            .ok_or_else(|| anyhow::anyhow!("App path has no parent"))?;

        // Находим точку входа
        let entry_point = if self.app_path.exists() && self.app_path.is_file() {
            // Если app_path указывает на конкретный файл, используем его
            self.app_path.clone()
        } else {
            // Иначе ищем стандартную точку входа
            self.core_builder.find_entry_point(project_root)?
        };

        // Строим граф вызовов от точки входа
        // CallGraphBuilder автоматически обработает:
        // - Импорты
        // - Функции и классы
        // - Вызовы функций
        // - Декораторы FastAPI (@app.get, @app.post и т.д.)
        self.core_builder.build_from_entry(&entry_point)?;

        // Возвращаем построенный граф
        Ok(self.core_builder.into_graph())
    }
}
