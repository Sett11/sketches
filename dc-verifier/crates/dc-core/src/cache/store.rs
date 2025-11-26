use crate::call_graph::{CallEdge, CallGraph, CallNode};
use anyhow::Result;
use blake3;
use bincode;
use sled::Db;

/// Хранилище кэша для графов вызовов
pub struct CacheStore {
    db: Db,
}

impl CacheStore {
    /// Создает новое хранилище кэша
    pub fn new(path: &str) -> Result<Self> {
        let db = sled::open(path)?;
        Ok(Self { db })
    }

    /// Проверяет, изменился ли граф для файла
    pub fn is_changed(&self, file_path: &str, content: &[u8]) -> Result<bool> {
        let key = format!("file:{}", file_path);
        let new_hash = blake3::hash(content);

        match self.db.get(&key)? {
            Some(old_hash) => Ok(old_hash.as_ref() != new_hash.as_bytes()),
            None => Ok(true), // Файл новый, значит изменился
        }
    }

    /// Сохраняет хеш файла
    pub fn save_file_hash(&self, file_path: &str, content: &[u8]) -> Result<()> {
        let key = format!("file:{}", file_path);
        let hash = blake3::hash(content);
        self.db.insert(key, hash.as_bytes())?;
        Ok(())
    }

    /// Сохраняет граф вызовов
    pub fn save_graph(&self, graph_id: &str, graph: &CallGraph) -> Result<()> {
        // Сериализуем граф вручную, так как petgraph::Graph не сериализуем напрямую
        // 1. Собираем все узлы
        let mut nodes: Vec<(u32, CallNode)> = Vec::new();
        for node_idx in graph.node_indices() {
            if let Some(node) = graph.node_weight(node_idx) {
                nodes.push((node_idx.index() as u32, node.clone()));
            }
        }

        // 2. Собираем все рёбра
        let mut edges: Vec<(u32, u32, CallEdge)> = Vec::new();
        for edge_idx in graph.edge_indices() {
            if let Some((source, target)) = graph.edge_endpoints(edge_idx) {
                if let Some(edge) = graph.edge_weight(edge_idx) {
                    edges.push((
                        source.index() as u32,
                        target.index() as u32,
                        edge.clone(),
                    ));
                }
            }
        }

        // 3. Создаем структуру для сериализации
        #[derive(serde::Serialize)]
        struct GraphData {
            nodes: Vec<(u32, CallNode)>,
            edges: Vec<(u32, u32, CallEdge)>,
        }

        let graph_data = GraphData { nodes, edges };

        // 4. Сериализуем через bincode
        let serialized = bincode::serialize(&graph_data)?;

        // 5. Сохраняем в sled
        let key = format!("graph:{}", graph_id);
        self.db.insert(key, serialized)?;

        Ok(())
    }

    /// Загружает граф вызовов
    pub fn load_graph(&self, graph_id: &str) -> Result<Option<CallGraph>> {
        let key = format!("graph:{}", graph_id);

        if let Some(data) = self.db.get(&key)? {
            // Десериализуем структуру
            #[derive(serde::Deserialize)]
            struct GraphData {
                nodes: Vec<(u32, CallNode)>,
                edges: Vec<(u32, u32, CallEdge)>,
            }

            let graph_data: GraphData = bincode::deserialize(data.as_ref())?;

            // Восстанавливаем граф
            let mut graph = CallGraph::new();

            // Создаем маппинг старых индексов на новые
            let mut index_map: std::collections::HashMap<u32, petgraph::graph::NodeIndex> =
                std::collections::HashMap::new();

            // Добавляем узлы
            for (old_idx, node) in graph_data.nodes {
                let new_idx = graph.add_node(node);
                index_map.insert(old_idx, new_idx);
            }

            // Добавляем рёбра
            for (source_old, target_old, edge) in graph_data.edges {
                if let (Some(&source_new), Some(&target_new)) =
                    (index_map.get(&source_old), index_map.get(&target_old))
                {
                    graph.add_edge(source_new, target_new, edge);
                }
            }

            Ok(Some(graph))
        } else {
            Ok(None)
        }
    }
}
