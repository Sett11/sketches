use crate::models::{BaseType, Constraint, SchemaReference, SchemaType};
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
        let mut required = Vec::new();

        // Пытаемся извлечь информацию из метаданных
        if let Some(fields_str) = schema_ref.metadata.get("fields") {
            // Парсинг полей из метаданных: разделяем только по первому ':'
            for field in fields_str.split(',') {
                let field = field.trim();
                if field.is_empty() {
                    continue;
                }
                
                // Разделяем только по первому ':'
                if let Some(colon_pos) = field.find(':') {
                    let name = field[..colon_pos].trim().to_string();
                    let field_type = field[colon_pos + 1..].trim().to_string();
                    
                    // Пропускаем пустые имена или типы
                    if name.is_empty() || field_type.is_empty() {
                        continue;
                    }
                    
                    // По умолчанию поле обязательное (добавим в required)
                    required.push(name.clone());
                    
                    properties.insert(
                        name.clone(),
                        FieldInfo {
                            field_type: field_type.clone(),
                            base_type: Self::base_type_from_string(&field_type),
                            optional: false, // Будет установлено ниже на основе required
                            constraints: Vec::new(),
                            nested_schema: None,
                        },
                    );
                }
            }
        }
        
        // Синхронизируем optional и required: если required пустой, все поля optional=true
        // Иначе устанавливаем optional=false для полей в required
        if required.is_empty() {
            // Если required пустой, все поля optional
            for field_info in properties.values_mut() {
                field_info.optional = true;
            }
        } else {
            // Устанавливаем optional=false для полей в required
            for field_name in &required {
                if let Some(field_info) = properties.get_mut(field_name) {
                    field_info.optional = false;
                }
            }
            // Остальные поля optional=true
            for (field_name, field_info) in properties.iter_mut() {
                if !required.contains(field_name) {
                    field_info.optional = true;
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
    fn parse_json_schema(_schema_ref: &SchemaReference) -> Result<JsonSchema> {
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
            "int" | "integer" => BaseType::Integer,
            "number" | "float" | "double" => BaseType::Number,
            "bool" | "boolean" => BaseType::Boolean,
            "list" | "array" => BaseType::Array,
            "dict" | "object" => BaseType::Object,
            "null" | "none" => BaseType::Null,
            _ => BaseType::Unknown,
        }
    }
}

