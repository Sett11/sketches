use anyhow::Result;
use serde::Deserialize;
use std::fs;
use std::path::Path;

/// Конфигурация проекта
#[derive(Debug, Deserialize)]
pub struct Config {
    pub project_name: String,
    pub entry_point: Option<String>,
    pub adapters: Vec<AdapterConfig>,
    pub rules: Option<RulesConfig>,
    pub output: OutputConfig,
}

/// Конфигурация адаптера
#[derive(Debug, Deserialize)]
pub struct AdapterConfig {
    #[serde(rename = "type")]
    pub adapter_type: String,
    pub app_path: Option<String>,
    pub src_paths: Option<Vec<String>>,
}

/// Конфигурация правил
#[derive(Debug, Deserialize)]
pub struct RulesConfig {
    pub type_mismatch: Option<String>,
    pub missing_field: Option<String>,
    pub unnormalized_data: Option<String>,
}

/// Конфигурация вывода
#[derive(Debug, Deserialize)]
pub struct OutputConfig {
    pub format: String,
    pub path: String,
}

impl Config {
    /// Загружает конфигурацию из файла
    pub fn load(path: &str) -> Result<Self> {
        let content = fs::read_to_string(Path::new(path))?;
        let config: Config = toml::from_str(&content)?;
        Ok(config)
    }
}
