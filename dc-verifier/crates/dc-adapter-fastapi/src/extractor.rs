use anyhow::Result;
use pyo3::prelude::*;
use pyo3::types::PyAny;
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
    pub fn load_app(&self) -> Result<Py<PyAny>> {
        Python::attach(|py| {
            // Dynamic import of FastAPI app using importlib
            let importlib = py.import("importlib.util")?;
            let spec_from_file = importlib.getattr("spec_from_file_location")?;
            let module_from_spec = importlib.getattr("module_from_spec")?;

            // Создаем spec из файла
            let app_path_str = self.app_path.to_str().ok_or_else(|| {
                anyhow::anyhow!("App path contains invalid UTF-8: {:?}", self.app_path)
            })?;
            let spec = spec_from_file.call1(("app", app_path_str))?;

            // Получаем loader до перемещения spec
            let loader = spec.getattr("loader")?;
            let module = module_from_spec.call1((spec,))?;

            // Загружаем модуль
            loader.call_method1("exec_module", (module.clone(),))?;

            // Получаем app
            let app = module.getattr("app")?;
            Ok(app.into())
        })
    }

    /// Извлекает routes из FastAPI app
    pub fn extract_routes(&self, app: &Bound<'_, PyAny>) -> Result<Vec<FastApiRoute>> {
        Python::attach(|py| {
            // Получаем routes из app
            let routes = app.getattr("routes")?;
            let routes_list: Vec<Py<PyAny>> = routes.extract()?;

            let mut result = Vec::new();

            // Импортируем APIRoute для проверки типа
            let fastapi_routing = py.import("fastapi.routing")?;
            let api_route_class = fastapi_routing.getattr("APIRoute")?;

            // Импортируем inspect для получения информации о файле
            let inspect = py.import("inspect")?;
            let getfile = inspect.getattr("getfile")?;
            let getsourcelines = inspect.getattr("getsourcelines")?;

            for route in routes_list {
                let route_bound = route.bind(py);

                // Проверяем, является ли это APIRoute
                let is_api_route = route_bound.is_instance(api_route_class.as_ref())?;
                if !is_api_route {
                    continue;
                }

                // Извлекаем path
                let path: String = route_bound.getattr("path")?.extract()?;

                // Извлекаем methods
                let methods_attr = route_bound.getattr("methods")?;
                let methods: Option<Vec<String>> = methods_attr.extract().ok();
                let method = methods
                    .and_then(|m| m.first().cloned())
                    .unwrap_or_else(|| "GET".to_string());

                // Извлекаем endpoint
                let endpoint = route_bound.getattr("endpoint")?;
                let handler: String = endpoint.getattr("__name__")?.extract()?;

                // Получаем информацию о файле и строке
                let (handler_file, handler_line) = match getfile.call1((endpoint.clone(),)) {
                    Ok(file_obj) => {
                        let file_str: String = file_obj.extract()?;
                        let file_path = PathBuf::from(file_str);

                        // Получаем номер строки
                        let line = match getsourcelines.call1((endpoint,)) {
                            Ok(lines_tuple) => {
                                let lines: (Vec<String>, usize) = lines_tuple.extract()?;
                                lines.1
                            }
                            Err(_) => 0,
                        };

                        (file_path, line)
                    }
                    Err(_) => {
                        // Если не удается получить файл, используем app_path
                        (self.app_path.clone(), 0)
                    }
                };

                result.push(FastApiRoute {
                    path,
                    method,
                    handler,
                    handler_file,
                    handler_line,
                });
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
