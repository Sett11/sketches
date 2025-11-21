use crate::models::Location;

/// Декоратор функции (для Python)
#[derive(Debug, Clone)]
pub struct Decorator {
    /// Имя декоратора (например, "app.post")
    pub name: String,
    /// Аргументы декоратора
    pub arguments: Vec<String>,
    /// Расположение в коде
    pub location: Location,
    /// Имя функции, к которой применяется декоратор
    pub target_function: Option<String>,
}


