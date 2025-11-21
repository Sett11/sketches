use crate::models::{Location, NodeId, TypeInfo};
use serde::{Deserialize, Serialize};
use std::path::PathBuf;

/// Узел в графе вызовов - представляет функцию, класс, метод или route
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum CallNode {
    /// Модуль (отдельный файл Python/TypeScript)
    Module {
        /// Путь к файлу модуля
        path: PathBuf,
    },
    /// Функция
    Function {
        /// Имя функции
        name: String,
        /// Файл, в котором определена функция
        file: PathBuf,
        /// Номер строки определения
        line: usize,
        /// Параметры функции
        parameters: Vec<Parameter>,
        /// Тип возвращаемого значения (если известен)
        return_type: Option<TypeInfo>,
    },
    /// Класс
    Class {
        /// Имя класса
        name: String,
        /// Файл, в котором определен класс
        file: PathBuf,
        /// Ссылки на методы класса
        methods: Vec<NodeId>,
    },
    /// Метод класса
    Method {
        /// Имя метода
        name: String,
        /// Ссылка на класс-владелец
        class: NodeId,
        /// Параметры метода
        parameters: Vec<Parameter>,
        /// Тип возвращаемого значения
        return_type: Option<TypeInfo>,
    },
    /// API Route (FastAPI, Express и т.д.)
    Route {
        /// Путь route (например, "/api/auth/login")
        path: String,
        /// HTTP метод
        method: HttpMethod,
        /// Ссылка на handler функцию
        handler: NodeId,
        /// Расположение в коде
        location: Location,
    },
}

/// Параметр функции/метода
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Parameter {
    /// Имя параметра
    pub name: String,
    /// Тип параметра
    pub type_info: TypeInfo,
    /// Является ли опциональным
    pub optional: bool,
    /// Значение по умолчанию (если есть)
    pub default_value: Option<String>,
}

/// HTTP метод
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum HttpMethod {
    Get,
    Post,
    Put,
    Patch,
    Delete,
    Options,
    Head,
}

impl HttpMethod {
    pub fn from_str(s: &str) -> Option<Self> {
        match s.to_uppercase().as_str() {
            "GET" => Some(HttpMethod::Get),
            "POST" => Some(HttpMethod::Post),
            "PUT" => Some(HttpMethod::Put),
            "PATCH" => Some(HttpMethod::Patch),
            "DELETE" => Some(HttpMethod::Delete),
            "OPTIONS" => Some(HttpMethod::Options),
            "HEAD" => Some(HttpMethod::Head),
            _ => None,
        }
    }
}
