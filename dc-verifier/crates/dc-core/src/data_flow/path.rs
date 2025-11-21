use crate::data_flow::Variable;
use crate::models::NodeId;
use serde::{Deserialize, Serialize};

/// Путь данных через граф вызовов
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DataPath {
    /// Начальный узел (источник данных)
    pub from: NodeId,
    /// Конечный узел (приемник данных)
    pub to: NodeId,
    /// Последовательность узлов в пути
    pub nodes: Vec<NodeId>,
    /// Переменная, которая передается по пути
    pub variable: Variable,
}

impl DataPath {
    /// Создает новый путь данных
    pub fn new(from: NodeId, to: NodeId, variable: Variable) -> Self {
        Self {
            from,
            to,
            nodes: vec![from, to],
            variable,
        }
    }

    /// Добавляет промежуточный узел в путь
    pub fn add_node(&mut self, node: NodeId) {
        if !self.nodes.contains(&node) {
            self.nodes.push(node);
        }
    }
}
