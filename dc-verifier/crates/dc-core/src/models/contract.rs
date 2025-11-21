use crate::models::{Location, SchemaReference, TypeInfo};
use serde::{Deserialize, Serialize};

/// Контракт между двумя звеньями цепочки
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Contract {
    /// Идентификатор звена-источника
    pub from_link_id: String,
    /// Идентификатор звена-приемника
    pub to_link_id: String,
    /// Схема данных источника
    pub from_schema: SchemaReference,
    /// Схема данных приемника
    pub to_schema: SchemaReference,
    /// Обнаруженные несоответствия
    pub mismatches: Vec<Mismatch>,
    /// Серьезность проблем в контракте
    pub severity: Severity,
}

/// Обнаруженное несоответствие на стыке
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Mismatch {
    /// Тип несоответствия
    pub mismatch_type: MismatchType,
    /// Путь к полю (например, "discount" или "client_data.full_name")
    pub path: String,
    /// Ожидаемый тип/значение
    pub expected: TypeInfo,
    /// Фактический тип/значение
    pub actual: TypeInfo,
    /// Расположение в коде
    pub location: Location,
    /// Сообщение об ошибке
    pub message: String,
}

/// Тип несоответствия
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum MismatchType {
    /// Несоответствие типов (например, number vs string)
    TypeMismatch,
    /// Отсутствующее обязательное поле
    MissingField,
    /// Лишнее поле
    ExtraField,
    /// Несоответствие валидации (например, min/max)
    ValidationMismatch,
    /// Ненормализованные данные
    UnnormalizedData,
}

/// Серьезность проблемы
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize)]
pub enum Severity {
    /// Информация (не критично)
    Info,
    /// Предупреждение (может вызвать проблемы)
    Warning,
    /// Критическая проблема (вызовет ошибку)
    Critical,
}
