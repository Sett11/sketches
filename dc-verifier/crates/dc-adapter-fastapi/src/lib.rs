use dc_core::models::DataChain;
use pyo3::prelude::*;

mod call_graph;
mod extractor;
mod pydantic;

pub use call_graph::*;
pub use extractor::*;
pub use pydantic::*;

/// Python модуль для FastAPI адаптера
#[pymodule]
fn dc_adapter_fastapi(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<FastApiAdapter>()?;
    Ok(())
}

/// Адаптер для FastAPI приложений
#[pyclass]
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
    fn extract_chains(&self) -> PyResult<Vec<DataChain>> {
        // TODO: Реализовать извлечение цепочек
        Ok(Vec::new())
    }
}
