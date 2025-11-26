use dc_core::models::DataChain;
use pyo3::prelude::*;
use serde_json;

mod call_graph;
mod extractor;
mod pydantic;

pub use call_graph::*;
pub use extractor::*;
pub use pydantic::*;

/// Python модуль для FastAPI адаптера
#[pymodule]
fn dc_adapter_fastapi(_py: Python, m: Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<FastApiAdapter>()?;
    Ok(())
}

/// Адаптер для FastAPI приложений
#[pyclass]
#[allow(dead_code)]
pub struct FastApiAdapter {
    app_path: String,
}

#[pymethods]
impl FastApiAdapter {
    #[new]
    fn new(app_path: String) -> Self {
        Self { app_path }
    }

    /// Извлекает цепочки данных из FastAPI приложения
    /// Возвращает JSON строку с цепочками данных
    /// Note: Chain extraction is currently handled by the CLI, not through this Python interface
    fn extract_chains(&self, py: Python) -> PyResult<Py<PyAny>> {
        let chains: Vec<DataChain> = Vec::new();
        
        // Сериализуем в JSON и возвращаем как Python объект
        let json_str = serde_json::to_string(&chains)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(
                format!("Failed to serialize chains: {}", e)
            ))?;
        
        // Парсим JSON в Python dict/list
        let json_module = py.import("json")?;
        let json_dict = json_module.call_method1("loads", (json_str,))?;
        Ok(json_dict.into())
    }
}
