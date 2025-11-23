use anyhow::Result;
use dc_core::models::{Location, SchemaReference, SchemaType};
use dc_core::parsers::{LocationConverter, PythonParser};
use pyo3::prelude::*;
use rustpython_parser::{parse, Mode};
use std::fs;
use std::path::Path;

/// Извлекатель Pydantic моделей
pub struct PydanticExtractor;

impl PydanticExtractor {
    /// Создает новый экстрактор
    pub fn new() -> Self {
        Self
    }

    /// Извлекает Pydantic модель из параметра функции
    pub fn extract_from_parameter(&self, param: &PyObject) -> Option<SchemaReference> {
        Python::with_gil(|py| {
            // TODO: Извлечь Pydantic модель из параметра
            // Проверяем, является ли параметр Pydantic моделью
            // Если да, извлекаем схему через model_json_schema()
            None
        })
    }

    /// Извлекает все Pydantic модели из файла
    pub fn extract_from_file(&self, path: &Path) -> Result<Vec<SchemaReference>> {
        // Читаем файл
        let source = fs::read_to_string(path)?;
        
        // Парсим AST
        let ast = parse(
            &source,
            Mode::Module,
            path.to_string_lossy().as_ref(),
        )?;
        
        // Создаем LocationConverter для точной конвертации байтовых смещений
        let converter = LocationConverter::new(source);
        
        // Используем PythonParser для извлечения моделей
        let parser = PythonParser::new();
        let file_path = path.to_string_lossy().to_string();
        Ok(parser.extract_pydantic_models(&ast, &file_path, &converter))
    }

    /// Преобразует Pydantic модель в SchemaReference
    pub fn model_to_schema(&self, model: &PyObject, location: Location) -> Result<SchemaReference> {
        Python::with_gil(|py| {
            // Получаем имя модели
            let name = model
                .getattr(py, "__name__")?
                .and_then(|n| n.extract::<String>(py).ok())
                .unwrap_or_else(|| "Unknown".to_string());

            // Получаем JSON схему
            let json_schema = model.call_method0(py, "model_json_schema")?;

            Ok(SchemaReference {
                name,
                schema_type: SchemaType::Pydantic,
                location,
                metadata: std::collections::HashMap::new(),
            })
        })
    }
}

impl Default for PydanticExtractor {
    fn default() -> Self {
        Self::new()
    }
}
