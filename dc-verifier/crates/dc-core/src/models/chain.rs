use crate::models::{Contract, Location, SchemaReference};
use petgraph::graph::NodeIndex;
use serde::{Deserialize, Deserializer, Serialize, Serializer};
use std::ops::Deref;

/// Направление цепочки данных
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum ChainDirection {
    /// Frontend → Backend → Database
    FrontendToBackend,
    /// Database → Backend → Frontend
    BackendToFrontend,
}

/// Основная модель цепочки данных
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DataChain {
    /// Уникальный идентификатор цепочки (например, "auth-login")
    pub id: String,
    /// Человекочитаемое имя цепочки (например, "User authentication flow")
    pub name: String,
    /// Звенья цепочки (последовательность узлов в графе)
    pub links: Vec<Link>,
    /// Контракты между звеньями (проверки на стыках)
    pub contracts: Vec<Contract>,
    /// Направление потока данных
    pub direction: ChainDirection,
}

/// Звено цепочки - один узел в графе вызовов
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Link {
    /// Уникальный идентификатор звена (например, "frontend-form")
    pub id: String,
    /// Тип звена в цепочке
    pub link_type: LinkType,
    /// Расположение в коде (файл и строка)
    pub location: Location,
    /// Ссылка на узел в графе вызовов
    pub node_id: NodeId,
    /// Схема данных на этом звене
    pub schema_ref: SchemaReference,
}

/// Тип звена в цепочке
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum LinkType {
    /// Источник данных (например, форма на фронтенде)
    Source,
    /// Трансформатор данных (например, валидация, нормализация)
    Transformer,
    /// Приемник данных (например, сохранение в БД)
    Sink,
}

/// Идентификатор узла в графе вызовов
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct NodeId(pub NodeIndex<u32>);

impl From<NodeIndex<u32>> for NodeId {
    fn from(idx: NodeIndex<u32>) -> Self {
        NodeId(idx)
    }
}

impl From<NodeId> for NodeIndex<u32> {
    fn from(node_id: NodeId) -> Self {
        node_id.0
    }
}

impl NodeId {
    pub fn index(&self) -> usize {
        self.0.index()
    }
}

impl Deref for NodeId {
    type Target = NodeIndex<u32>;

    fn deref(&self) -> &Self::Target {
        &self.0
    }
}

impl Serialize for NodeId {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        serializer.serialize_u32(self.0.index() as u32)
    }
}

impl<'de> Deserialize<'de> for NodeId {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: Deserializer<'de>,
    {
        let idx = u32::deserialize(deserializer)?;
        Ok(NodeId(NodeIndex::new(idx as usize)))
    }
}
