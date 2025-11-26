use serde::{Deserialize, Serialize};

/// Расположение в коде
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, Hash)]
pub struct Location {
    /// Путь к файлу
    pub file: String,
    /// Номер строки (1-based)
    pub line: usize,
    /// Номер колонки (опционально, 1-based)
    pub column: Option<usize>,
}
