pub mod location;
pub mod openapi;
pub mod python;
pub mod typescript;

pub use location::*;
pub use openapi::*;
pub use python::*;
pub use typescript::*;

/// Импорт модуля/функции
#[derive(Debug, Clone)]
pub struct Import {
    /// Путь импорта (например, "fastapi" или "db.crud")
    pub path: String,
    /// Импортируемые имена (если есть)
    pub names: Vec<String>,
    /// Расположение в коде
    pub location: crate::models::Location,
}

/// Вызов функции
#[derive(Debug, Clone)]
pub struct Call {
    /// Имя вызываемой функции
    pub name: String,
    /// Аргументы вызова
    pub arguments: Vec<CallArgument>,
    /// Расположение в коде
    pub location: crate::models::Location,
    /// Имя функции/метода, внутри которой находится вызов
    pub caller: Option<String>,
}

/// Аргумент вызова функции
#[derive(Debug, Clone)]
pub struct CallArgument {
    /// Имя параметра (если именованный)
    pub parameter_name: Option<String>,
    /// Значение аргумента (имя переменной или выражение)
    pub value: String,
}
