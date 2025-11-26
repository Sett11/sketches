use crate::data_flow::Variable;
use crate::models::NodeId;
use serde::{Deserialize, Serialize};

/// Ошибки, связанные с DataPath
#[derive(Debug, Clone)]
pub enum DataPathError {
    /// Попытка установить пустой список узлов
    EmptyNodes,
    /// Попытка установить путь короче двух узлов
    InsufficientNodes,
}

/// Путь данных через граф вызовов
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DataPath {
    /// Последовательность узлов в пути
    nodes: Vec<NodeId>,
    /// Переменная, которая передается по пути
    variable: Variable,
}

impl DataPath {
    /// Создает новый путь данных
    /// Требует непустой список узлов (минимум from и to)
    pub fn new(from: NodeId, to: NodeId, variable: Variable) -> Self {
        Self {
            nodes: vec![from, to],
            variable,
        }
    }

    /// Возвращает начальный узел (источник данных)
    pub fn from(&self) -> Option<&NodeId> {
        self.nodes.first()
    }

    /// Возвращает конечный узел (приемник данных)
    pub fn to(&self) -> Option<&NodeId> {
        self.nodes.last()
    }

    /// Возвращает последовательность узлов
    pub fn nodes(&self) -> &[NodeId] {
        &self.nodes
    }

    /// Возвращает переменную
    pub fn variable(&self) -> &Variable {
        &self.variable
    }

    /// Добавляет промежуточный узел в путь
    pub fn push_node(&mut self, node: NodeId) {
        if !self.nodes.contains(&node) {
            self.nodes.push(node);
        }
    }

    /// Устанавливает последовательность узлов с сохранением консистентности
    ///
    /// # Ошибки
    ///
    /// Возвращает `Err(DataPathError::InsufficientNodes)`, если передано меньше двух узлов.
    pub fn set_nodes(&mut self, nodes: Vec<NodeId>) -> Result<(), DataPathError> {
        if nodes.is_empty() {
            return Err(DataPathError::EmptyNodes);
        }
        if nodes.len() < 2 {
            return Err(DataPathError::InsufficientNodes);
        }
        self.nodes = nodes;
        Ok(())
    }
}
