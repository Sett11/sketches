use crate::models::{BaseType, Constraint, ConstraintValue, SchemaReference, SchemaType};
use anyhow::Result;
use serde_json::Value;
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
        // Проверяем, есть ли полная JSON схема в metadata
        if let Some(json_schema_str) = schema_ref.metadata.get("json_schema") {
            // Используем полную JSON схему
            let json_value: Value = serde_json::from_str(json_schema_str)?;
            let mut schema = Self::parse_json_value(&json_value)?;
            
            // Синхронизируем optional флаги с required
            for (field_name, field_info) in schema.properties.iter_mut() {
                field_info.optional = !schema.required.contains(field_name);
            }
            
            return Ok(schema);
        }

        // Fallback: используем метаданные
        let mut properties = HashMap::new();
        let mut required = Vec::new();

        // Извлекаем required из metadata, если есть
        if let Some(required_str) = schema_ref.metadata.get("required") {
            for field in required_str.split(',') {
                let field = field.trim();
                if !field.is_empty() {
                    required.push(field.to_string());
                }
            }
        }

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
                    
                    properties.insert(
                        name.clone(),
                        FieldInfo {
                            field_type: field_type.clone(),
                            base_type: Self::base_type_from_string(&field_type),
                            optional: true, // По умолчанию поля опциональны
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
        // Проверяем, есть ли JSON схема в metadata (если TypeScript схема была конвертирована)
        if let Some(json_schema_str) = schema_ref.metadata.get("json_schema") {
            let json_value: Value = serde_json::from_str(json_schema_str)?;
            let mut schema = Self::parse_json_value(&json_value)?;
            
            // Синхронизируем optional флаги с required
            for (field_name, field_info) in schema.properties.iter_mut() {
                field_info.optional = !schema.required.contains(field_name);
            }
            
            return Ok(schema);
        }

        // Извлекаем поля из metadata (формат: "name:type:optional" или "name:type")
        let mut properties = HashMap::new();
        let mut required = Vec::new();

        if let Some(fields_str) = schema_ref.metadata.get("fields") {
            for field in fields_str.split(',') {
                let field = field.trim();
                if field.is_empty() {
                    continue;
                }
                
                // Разделяем по ':'
                let parts: Vec<&str> = field.split(':').collect();
                if parts.len() >= 2 {
                    let name = parts[0].trim().to_string();
                    let field_type = parts[1].trim().to_string();
                    let optional = parts.get(2).map(|s| s.trim() == "optional").unwrap_or(false);
                    
                    if !name.is_empty() && !field_type.is_empty() {
                        let base_type = Self::base_type_from_string(&field_type);
                        let field_info = FieldInfo {
                            field_type,
                            base_type,
                            optional,
                            constraints: Vec::new(),
                            nested_schema: None,
                        };
                        properties.insert(name.clone(), field_info);
                        
                        if !optional {
                            required.push(name);
                        }
                    }
                }
            }
        }

        // Если есть тип в metadata (для type aliases)
        if let Some(type_str) = schema_ref.metadata.get("type") {
            let base_type = Self::base_type_from_string(type_str);
            let schema_type = match base_type {
                BaseType::String => "string",
                BaseType::Number => "number",
                BaseType::Integer => "integer",
                BaseType::Boolean => "boolean",
                BaseType::Object => "object",
                BaseType::Array => "array",
                BaseType::Null => "null",
                BaseType::Any => "any",
                BaseType::Unknown => "unknown",
            };
            return Ok(JsonSchema {
                schema_type: schema_type.to_string(),
                properties: HashMap::new(),
                required: Vec::new(),
                items: None,
                constraints: Vec::new(),
            });
        }

        Ok(JsonSchema {
            schema_type: "object".to_string(),
            properties,
            required,
            items: None,
            constraints: Vec::new(),
        })
    }

    /// Парсит OpenAPI схему
    fn parse_openapi(schema_ref: &SchemaReference) -> Result<JsonSchema> {
        Self::parse_json_schema(schema_ref)
    }

    /// Парсит JSON Schema
    fn parse_json_schema(schema_ref: &SchemaReference) -> Result<JsonSchema> {
        // Извлекаем JSON Schema из metadata
        let json_schema_str = schema_ref
            .metadata
            .get("json_schema")
            .ok_or_else(|| anyhow::anyhow!("JSON schema not found in metadata"))?;

        // Десериализуем JSON
        let json_value: Value = serde_json::from_str(json_schema_str)?;

        Self::parse_json_value(&json_value)
    }

    /// Парсит JSON Schema из Value
    fn parse_json_value(json_value: &Value) -> Result<JsonSchema> {
        let schema_type = json_value
            .get("type")
            .and_then(|v| v.as_str())
            .unwrap_or("object")
            .to_string();

        let mut properties = HashMap::new();
        let mut required = Vec::new();
        let mut constraints = Vec::new();

        // Извлекаем properties для объектов
        if let Some(props) = json_value.get("properties").and_then(|v| v.as_object()) {
            for (name, prop_value) in props {
                let field_info = Self::parse_property(prop_value)?;
                properties.insert(name.clone(), field_info);
            }
        }

        // Извлекаем required поля
        if let Some(req) = json_value.get("required").and_then(|v| v.as_array()) {
            for field in req {
                if let Some(name) = field.as_str() {
                    required.push(name.to_string());
                }
            }
        }

        // Извлекаем constraints
        if let Some(min) = json_value.get("minimum").and_then(|v| v.as_f64()) {
            constraints.push(Constraint::Min(ConstraintValue::Float(min)));
        }
        if let Some(max) = json_value.get("maximum").and_then(|v| v.as_f64()) {
            constraints.push(Constraint::Max(ConstraintValue::Float(max)));
        }
        if let Some(min_len) = json_value.get("minLength").and_then(|v| v.as_u64()) {
            constraints.push(Constraint::Min(ConstraintValue::Integer(min_len as i64)));
        }
        if let Some(max_len) = json_value.get("maxLength").and_then(|v| v.as_u64()) {
            constraints.push(Constraint::Max(ConstraintValue::Integer(max_len as i64)));
        }
        if let Some(pattern) = json_value.get("pattern").and_then(|v| v.as_str()) {
            constraints.push(Constraint::Pattern(pattern.to_string()));
        }
        if json_value.get("format").and_then(|v| v.as_str()) == Some("email") {
            constraints.push(Constraint::Email);
        }
        if json_value.get("format").and_then(|v| v.as_str()) == Some("uri") {
            constraints.push(Constraint::Url);
        }
        if let Some(enum_values) = json_value.get("enum").and_then(|v| v.as_array()) {
            let enum_strings: Vec<String> = enum_values
                .iter()
                .filter_map(|v| v.as_str().map(|s| s.to_string()))
                .collect();
            if !enum_strings.is_empty() {
                constraints.push(Constraint::Enum(enum_strings));
            }
        }

        // Извлекаем items для массивов
        let items = if let Some(items_value) = json_value.get("items") {
            Some(Box::new(Self::parse_json_value(items_value)?))
        } else {
            None
        };

        Ok(JsonSchema {
            schema_type,
            properties,
            required,
            items,
            constraints,
        })
    }

    /// Парсит свойство из JSON Schema
    fn parse_property(prop_value: &Value) -> Result<FieldInfo> {
        let field_type = prop_value
            .get("type")
            .and_then(|v| v.as_str())
            .unwrap_or("any")
            .to_string();

        let base_type = Self::base_type_from_string(&field_type);

        let mut constraints = Vec::new();

        // Извлекаем constraints для поля
        if let Some(min) = prop_value.get("minimum").and_then(|v| v.as_f64()) {
            constraints.push(Constraint::Min(ConstraintValue::Float(min)));
        }
        if let Some(max) = prop_value.get("maximum").and_then(|v| v.as_f64()) {
            constraints.push(Constraint::Max(ConstraintValue::Float(max)));
        }
        if let Some(min_len) = prop_value.get("minLength").and_then(|v| v.as_u64()) {
            constraints.push(Constraint::Min(ConstraintValue::Integer(min_len as i64)));
        }
        if let Some(max_len) = prop_value.get("maxLength").and_then(|v| v.as_u64()) {
            constraints.push(Constraint::Max(ConstraintValue::Integer(max_len as i64)));
        }
        if let Some(pattern) = prop_value.get("pattern").and_then(|v| v.as_str()) {
            constraints.push(Constraint::Pattern(pattern.to_string()));
        }

        // Проверяем вложенную схему (для объектов)
        let nested_schema = if field_type == "object" {
            Some(Box::new(Self::parse_json_value(prop_value)?))
        } else {
            None
        };

        Ok(FieldInfo {
            field_type,
            base_type,
            optional: true, // Будет установлено позже на основе required
            constraints,
            nested_schema,
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

