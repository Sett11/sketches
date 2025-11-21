use crate::call_graph::CallGraph;
use anyhow::Result;
use blake3;
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
        // TODO: Сериализовать граф и сохранить
        let key = format!("graph:{}", graph_id);
        // self.db.insert(key, serialized_graph)?;
        Ok(())
    }

    /// Загружает граф вызовов
    pub fn load_graph(&self, graph_id: &str) -> Result<Option<CallGraph>> {
        // TODO: Загрузить и десериализовать граф
        let key = format!("graph:{}", graph_id);
        // if let Some(data) = self.db.get(key)? {
        //     Ok(Some(deserialize_graph(data.as_ref())?))
        // } else {
        //     Ok(None)
        // }
        Ok(None)
    }
}
