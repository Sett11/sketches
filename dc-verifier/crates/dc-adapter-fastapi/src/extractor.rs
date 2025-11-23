use anyhow::Result;
use pyo3::prelude::*;
use std::path::PathBuf;

/// Извлекает FastAPI приложение и routes
pub struct FastApiExtractor {
    app_path: PathBuf,
}

impl FastApiExtractor {
    /// Создает новый экстрактор
    pub fn new(app_path: PathBuf) -> Self {
        Self { app_path }
    }

    /// Загружает FastAPI app через PyO3
    pub fn load_app(&self) -> Result<PyObject> {
        Python::with_gil(|py| {
            // TODO: Динамический импорт FastAPI app
            // Используем importlib для загрузки модуля
            let importlib = py.import("importlib.util")?;
            let spec_from_file = importlib.getattr("spec_from_file_location")?;
            let module_from_spec = importlib.getattr("module_from_spec")?;

            // Создаем spec из файла
            let app_path_str = self.app_path.to_str().ok_or_else(|| {
                anyhow::anyhow!("App path contains invalid UTF-8: {:?}", self.app_path)
            })?;
            let spec = spec_from_file.call1(("app", app_path_str))?;
            let module = module_from_spec.call1((spec,))?;

            // Загружаем модуль
            let loader = spec.getattr("loader")?;
            loader.call_method1("exec_module", (module,))?;

            // Получаем app
            let app = module.getattr("app")?;
            Ok(app.to_object(py))
        })
    }

    /// Извлекает routes из FastAPI app
    pub fn extract_routes(&self, app: &PyObject) -> Result<Vec<FastApiRoute>> {
        Python::with_gil(|py| {
            let routes = app.getattr(py, "routes")?;
            let routes_list: Vec<PyObject> = routes.extract(py)?;

            let mut result = Vec::new();
            for route in routes_list {
                // TODO: Извлечь информацию о route
                // Проверяем, является ли это APIRoute
                let route_type = route.get_type(py);
                // ...
            }

            Ok(result)
        })
    }
}

/// FastAPI route
#[derive(Debug, Clone)]
pub struct FastApiRoute {
    pub path: String,
    pub method: String,
    pub handler: String,
    pub handler_file: PathBuf,
    pub handler_line: usize,
}
