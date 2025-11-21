use crate::models::{BaseType, Constraint, SchemaReference, SchemaType, TypeInfo};
use anyhow::Result;
use std::collections::HashMap;

/// Представление JSON Schema для сравнения
#[derive(Debug, Clone, PartialEq)]
pub struct JsonSchema {
    /// Тип схемы (object, array, string, number, etc.)
    pub schema_type: String,
    /// Поля объекта (для type="object")
    pub properties: HashMap<String, FieldInfo>,
    /// Обязательные поля
    pub required: Vec<String>,
    /// Элементы массива (для type="array")
    pub items: Option<Box<JsonSchema>>,
    /// Дополнительные ограничения
    pub constraints: Vec<Constraint>,
}

/// Информация о поле в схеме
#[derive(Debug, Clone, PartialEq)]
pub struct FieldInfo {
    /// Тип поля
    pub field_type: String,
    /// Базовый тип (для сравнения)
    pub base_type: BaseType,
    /// Является ли опциональным
    pub optional: bool,
    /// Ограничения/валидация
    pub constraints: Vec<Constraint>,
    /// Вложенная схема (для объектов)
    pub nested_schema: Option<Box<JsonSchema>>,
}

/// Парсер схем из SchemaReference
pub struct SchemaParser;

impl SchemaParser {
    /// Парсит SchemaReference в JsonSchema
    pub fn parse(schema_ref: &SchemaReference) -> Result<JsonSchema> {
        match schema_ref.schema_type {
            SchemaType::Pydantic => Self::parse_pydantic(schema_ref),
            SchemaType::Zod => Self::parse_zod(schema_ref),
            SchemaType::TypeScript => Self::parse_typescript(schema_ref),
            SchemaType::OpenAPI => Self::parse_openapi(schema_ref),
            SchemaType::JsonSchema => Self::parse_json_schema(schema_ref),
        }
    }

    /// Парсит Pydantic схему
    fn parse_pydantic(schema_ref: &SchemaReference) -> Result<JsonSchema> {
        // Пока создаем базовую схему из метаданных
        // TODO: На Этапе 5 добавим полное извлечение из Pydantic моделей
        let mut properties = HashMap::new();
        let required = Vec::new();

        // Пытаемся извлечь информацию из метаданных
        if let Some(fields_str) = schema_ref.metadata.get("fields") {
            // Простой парсинг полей из метаданных
            for field in fields_str.split(',') {
                let parts: Vec<&str> = field.split(':').collect();
                if parts.len() >= 2 {
                    let name = parts[0].trim().to_string();
                    let field_type = parts[1].trim().to_string();
                    properties.insert(
                        name.clone(),
                        FieldInfo {
                            field_type: field_type.clone(),
                            base_type: Self::base_type_from_string(&field_type),
                            optional: false,
                            constraints: Vec::new(),
                            nested_schema: None,
                        },
                    );
                }
            }
        }

        Ok(JsonSchema {
            schema_type: "object".to_string(),
            properties,
            required,
            items: None,
            constraints: Vec::new(),
        })
    }

    /// Парсит Zod схему
    fn parse_zod(schema_ref: &SchemaReference) -> Result<JsonSchema> {
        // Аналогично Pydantic
        Self::parse_pydantic(schema_ref)
    }

    /// Парсит TypeScript схему
    fn parse_typescript(schema_ref: &SchemaReference) -> Result<JsonSchema> {
        Self::parse_pydantic(schema_ref)
    }

    /// Парсит OpenAPI схему
    fn parse_openapi(schema_ref: &SchemaReference) -> Result<JsonSchema> {
        Self::parse_json_schema(schema_ref)
    }

    /// Парсит JSON Schema
    fn parse_json_schema(schema_ref: &SchemaReference) -> Result<JsonSchema> {
        // Пока создаем базовую схему
        // TODO: Полный парсинг JSON Schema будет на Этапе 5
        Ok(JsonSchema {
            schema_type: "object".to_string(),
            properties: HashMap::new(),
            required: Vec::new(),
            items: None,
            constraints: Vec::new(),
        })
    }

    /// Преобразует строковый тип в BaseType
    fn base_type_from_string(type_str: &str) -> BaseType {
        match type_str.to_lowercase().as_str() {
            "str" | "string" => BaseType::String,
            "int" | "integer" | "number" => BaseType::Integer,
            "float" | "double" => BaseType::Number,
            "bool" | "boolean" => BaseType::Boolean,
            "list" | "array" => BaseType::Array,
            "dict" | "object" => BaseType::Object,
            "null" | "none" => BaseType::Null,
            _ => BaseType::Unknown,
        }
    }
}

