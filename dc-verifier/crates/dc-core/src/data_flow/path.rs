use crate::data_flow::Variable;
use crate::models::NodeId;
use serde::{Deserialize, Serialize};

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
    pub fn set_nodes(&mut self, nodes: Vec<NodeId>) {
        if !nodes.is_empty() {
            self.nodes = nodes;
        }
    }
}
