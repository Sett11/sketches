use crate::extractor::FastApiExtractor;
use anyhow::Result;
use dc_core::call_graph::{CallGraph, CallGraphBuilder};
use std::path::{Path, PathBuf};

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
    /// Потребляет self, так как вызывает into_graph() на core_builder
    pub fn build_graph(self) -> Result<CallGraph> {
        // Определяем корень проекта
        let project_root = Self::find_project_root(&self.app_path);

        // Находим точку входа
        let entry_point = if self.app_path.exists() && self.app_path.is_file() {
            // Если app_path указывает на конкретный файл, используем его
            self.app_path.clone()
        } else {
            // Иначе ищем стандартную точку входа
            self.core_builder.find_entry_point(&project_root)?
        };

        // Строим граф вызовов от точки входа
        // CallGraphBuilder автоматически обработает:
        // - Импорты
        // - Функции и классы
        // - Вызовы функций
        // - Декораторы FastAPI (@app.get, @app.post и т.д.)
        let mut core_builder = self.core_builder;
        core_builder.build_from_entry(&entry_point)?;

        // Возвращаем построенный граф
        Ok(core_builder.into_graph())
    }

    /// Находит корень проекта, поднимаясь вверх от app_path и ища маркеры проекта
    fn find_project_root(app_path: &Path) -> PathBuf {
        let markers = ["pyproject.toml", "setup.py", "requirements.txt", ".git"];
        let mut current = app_path.to_path_buf();

        // Если app_path - это файл, начинаем с его родителя
        if current.is_file() {
            if let Some(parent) = current.parent() {
                current = parent.to_path_buf();
            }
        }

        // Поднимаемся вверх, пока не найдем маркер
        while let Some(parent) = current.parent() {
            // Проверяем наличие маркеров
            for marker in &markers {
                let marker_path = parent.join(marker);
                // Обрабатываем ошибки доступа gracefully
                if marker_path.exists() {
                    return parent.to_path_buf();
                }
            }
            current = parent.to_path_buf();
        }

        // Fallback: возвращаем родителя app_path или сам app_path
        app_path
            .parent()
            .map(|p| p.to_path_buf())
            .unwrap_or_else(|| app_path.to_path_buf())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;
    use tempfile::TempDir;

    #[test]
    fn test_find_project_root_with_pyproject() {
        let temp_dir = TempDir::new().unwrap();
        let project_root = temp_dir.path();
        let app_path = project_root.join("src").join("app.py");

        // Создаем структуру проекта
        fs::create_dir_all(app_path.parent().unwrap()).unwrap();
        fs::write(project_root.join("pyproject.toml"), "[project]").unwrap();
        fs::write(&app_path, "from fastapi import FastAPI").unwrap();

        let found_root = FastApiCallGraphBuilder::find_project_root(&app_path);
        assert_eq!(found_root, project_root);
    }

    #[test]
    fn test_find_project_root_with_git() {
        let temp_dir = TempDir::new().unwrap();
        let project_root = temp_dir.path();
        let app_path = project_root.join("backend").join("api").join("main.py");

        fs::create_dir_all(app_path.parent().unwrap()).unwrap();
        fs::create_dir_all(project_root.join(".git")).unwrap();
        fs::write(&app_path, "from fastapi import FastAPI").unwrap();

        let found_root = FastApiCallGraphBuilder::find_project_root(&app_path);
        assert_eq!(found_root, project_root);
    }

    #[test]
    fn test_find_project_root_fallback() {
        let temp_dir = TempDir::new().unwrap();
        let app_path = temp_dir.path().join("app.py");
        fs::write(&app_path, "from fastapi import FastAPI").unwrap();

        let found_root = FastApiCallGraphBuilder::find_project_root(&app_path);
        // Должен вернуть родителя app_path
        assert_eq!(found_root, app_path.parent().unwrap());
    }
}
