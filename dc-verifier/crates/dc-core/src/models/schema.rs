use crate::models::Location;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// Ссылка на схему данных
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct SchemaReference {
    /// Имя схемы (например, "UserLogin", "RegisterRequest")
    pub name: String,
    /// Тип схемы
    pub schema_type: SchemaType,
    /// Расположение схемы (файл и строка)
    pub location: Location,
    /// Дополнительные метаданные
    pub metadata: HashMap<String, String>,
}

/// Тип схемы
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum SchemaType {
    /// Pydantic модель (Python)
    Pydantic,
    /// Zod схема (TypeScript)
    Zod,
    /// TypeScript тип/интерфейс
    TypeScript,
    /// OpenAPI схема
    OpenAPI,
    /// JSON Schema
    JsonSchema,
}

/// Информация о типе данных
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct TypeInfo {
    /// Базовый тип
    pub base_type: BaseType,
    /// Ссылка на схему (если есть)
    pub schema_ref: Option<SchemaReference>,
    /// Ограничения/валидация
    pub constraints: Vec<Constraint>,
    /// Является ли опциональным
    pub optional: bool,
}

/// Базовый тип данных
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum BaseType {
    String,
    Number,
    Integer,
    Boolean,
    Object,
    Array,
    Null,
    Any,
    Unknown,
}

/// Ограничение/валидация для типа
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum Constraint {
    /// Минимальная длина (для строк) или значение (для чисел)
    Min(ConstraintValue),
    /// Максимальная длина (для строк) или значение (для чисел)
    Max(ConstraintValue),
    /// Регулярное выражение (для строк)
    Pattern(String),
    /// Email валидация
    Email,
    /// URL валидация
    Url,
    /// Enum значения
    Enum(Vec<String>),
}

/// Значение ограничения
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum ConstraintValue {
    Integer(i64),
    Float(f64),
}
