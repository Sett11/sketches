use crate::models::{Location, TypeInfo};
use serde::{Deserialize, Serialize};

/// Переменная в коде
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Variable {
    /// Имя переменной
    pub name: String,
    /// Информация о типе
    pub type_info: TypeInfo,
    /// Расположение в коде
    pub location: Location,
    /// Источник переменной
    pub source: VariableSource,
}

/// Источник переменной
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum VariableSource {
    /// Параметр функции
    Parameter,
    /// Возвращаемое значение функции
    Return,
    /// Импортированная переменная
    Import,
    /// Локальная переменная
    Local,
    /// Поле объекта
    Field,
}
