use anyhow::Result;
use dc_core::models::{Location, SchemaReference, SchemaType};
use dc_core::parsers::{LocationConverter, PythonParser};
use pyo3::prelude::*;
use pyo3::types::PyAny;
use rustpython_parser::{parse, Mode};
use std::fs;
use std::path::Path;

/// Извлекатель Pydantic моделей
pub struct PydanticExtractor;

impl PydanticExtractor {
    fn serialize_schema(py: Python<'_>, model: &Bound<'_, PyAny>) -> Option<String> {
        let schema = model.call_method0("model_json_schema").ok()?;
        let json_module = py.import("json").ok()?;
        let json_dumps = json_module.getattr("dumps").ok()?;
        json_dumps.call1((schema,)).ok()?.extract::<String>().ok()
    }

    /// Создает новый экстрактор
    pub fn new() -> Self {
        Self
    }

    /// Извлекает Pydantic модель из параметра функции
    pub fn extract_from_parameter(&self, param: &Bound<'_, PyAny>) -> Option<SchemaReference> {
        let py = param.py();
        // Параметр может быть:
        // 1. Классом Pydantic модели (тип аннотации)
        // 2. Экземпляром Pydantic модели

        // Импортируем BaseModel для проверки
        let pydantic = py.import("pydantic").ok()?;
        let base_model = pydantic.getattr("BaseModel").ok()?;

        // Проверяем, является ли параметр классом, наследующимся от BaseModel
        let is_base_model = match param.is_instance(base_model.as_ref()) {
            Ok(true) => true,
            Ok(false) => param.hasattr("model_json_schema").unwrap_or(false),
            Err(_) => false,
        };

        if !is_base_model {
            return None;
        }

        // Извлекаем имя модели
        let name = param
            .getattr("__name__")
            .and_then(|n| n.extract::<String>())
            .unwrap_or_else(|_| "Unknown".to_string());

        // Извлекаем JSON схему
        let json_schema_str = Self::serialize_schema(py, param).unwrap_or_else(|| "{}".to_string());

        // Извлекаем поля модели
        let mut metadata = std::collections::HashMap::new();
        metadata.insert("json_schema".to_string(), json_schema_str);

        // Пытаемся получить model_fields
        if let Ok(model_fields) = param.getattr("model_fields") {
            if let Ok(fields_dict) = model_fields.cast::<pyo3::types::PyDict>() {
                let mut fields = Vec::new();
                for (key, value) in fields_dict.iter() {
                    if let Ok(field_name) = key.extract::<String>() {
                        let field_info = value;
                        let field_type = field_info
                            .getattr("annotation")
                            .and_then(|annotation| {
                                annotation.repr().and_then(|r| r.extract::<String>())
                            })
                            .unwrap_or_else(|_| "Any".to_string());
                        fields.push(format!("{}:{}", field_name, field_type));
                    }
                }
                if !fields.is_empty() {
                    metadata.insert("fields".to_string(), fields.join(","));
                }
            }
        }

        Some(SchemaReference {
            name,
            schema_type: SchemaType::Pydantic,
            location: Location {
                file: String::new(), // Файл будет установлен позже
                line: 0,
                column: None,
            },
            metadata,
        })
    }

    /// Извлекает все Pydantic модели из файла
    pub fn extract_from_file(&self, path: &Path) -> Result<Vec<SchemaReference>> {
        // Читаем файл
        let source = fs::read_to_string(path)?;

        // Парсим AST
        let ast = parse(&source, Mode::Module, path.to_string_lossy().as_ref())?;

        // Создаем LocationConverter для точной конвертации байтовых смещений
        let converter = LocationConverter::new(source);

        // Используем PythonParser для извлечения моделей
        let parser = PythonParser::new();
        let file_path = path.to_string_lossy().to_string();
        Ok(parser.extract_pydantic_models(&ast, &file_path, &converter))
    }

    /// Преобразует Pydantic модель в SchemaReference
    pub fn model_to_schema(
        &self,
        model: &Bound<'_, PyAny>,
        location: Location,
    ) -> Result<SchemaReference> {
        let py = model.py();

        let name_attr = model.getattr("__name__")?;
        let name = name_attr
            .extract::<String>()
            .unwrap_or_else(|_| "Unknown".to_string());

        let mut metadata = std::collections::HashMap::new();
        if let Some(schema_str) = Self::serialize_schema(py, model) {
            metadata.insert("json_schema".to_string(), schema_str);
        }

        Ok(SchemaReference {
            name,
            schema_type: SchemaType::Pydantic,
            location,
            metadata,
        })
    }
}

impl Default for PydanticExtractor {
    fn default() -> Self {
        Self::new()
    }
}
