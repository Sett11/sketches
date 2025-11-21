use crate::models::NodeId;
use serde::{Deserialize, Serialize};
use std::path::PathBuf;

/// Ребро в графе вызовов - представляет связь между узлами
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum CallEdge {
    /// Импорт модуля/функции
    Import {
        /// Узел, который делает импорт
        from: NodeId,
        /// Узел, который импортируется
        to: NodeId,
        /// Путь импорта (например, "fastapi" или "db.crud")
        import_path: String,
        /// Файл, из которого импортируется
        file: PathBuf,
    },
    /// Вызов функции/метода
    Call {
        /// Узел, который вызывает (caller)
        caller: NodeId,
        /// Узел, который вызывается (callee)
        callee: NodeId,
        /// Маппинг аргументов: (имя_параметра, имя_переменной)
        argument_mapping: Vec<(String, String)>,
        /// Расположение вызова в коде
        location: crate::models::Location,
    },
    /// Возврат значения
    Return {
        /// Узел, который возвращает значение
        from: NodeId,
        /// Узел, который получает значение (caller)
        to: NodeId,
        /// Имя возвращаемой переменной
        return_value: String,
    },
}
