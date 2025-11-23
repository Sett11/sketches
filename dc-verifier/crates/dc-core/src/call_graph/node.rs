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
    /// Удобный метод для получения Option
    pub fn from_str_opt(s: &str) -> Option<Self> {
        s.parse().ok()
    }
}

impl std::str::FromStr for HttpMethod {
    type Err = ();

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        // Используем eq_ignore_ascii_case для избежания аллокации
        if s.eq_ignore_ascii_case("GET") {
            Ok(HttpMethod::Get)
        } else if s.eq_ignore_ascii_case("POST") {
            Ok(HttpMethod::Post)
        } else if s.eq_ignore_ascii_case("PUT") {
            Ok(HttpMethod::Put)
        } else if s.eq_ignore_ascii_case("PATCH") {
            Ok(HttpMethod::Patch)
        } else if s.eq_ignore_ascii_case("DELETE") {
            Ok(HttpMethod::Delete)
        } else if s.eq_ignore_ascii_case("OPTIONS") {
            Ok(HttpMethod::Options)
        } else if s.eq_ignore_ascii_case("HEAD") {
            Ok(HttpMethod::Head)
        } else {
            Err(())
        }
    }
}
