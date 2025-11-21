use crate::models::SchemaReference;
use anyhow::Result;
use serde_json::Value;

/// Парсер OpenAPI спецификаций для связывания frontend/backend
pub struct OpenApiParser {
    spec: Value,
}

impl OpenApiParser {
    /// Создает парсер из JSON строки
    pub fn from_json(spec_json: &str) -> Result<Self> {
        let spec: Value = serde_json::from_str(spec_json)?;
        Ok(Self { spec })
    }

    /// Извлекает все эндпоинты из спецификации
    pub fn extract_endpoints(&self) -> Vec<ApiEndpoint> {
        let mut endpoints = Vec::new();

        if let Some(paths) = self.spec.get("paths").and_then(|p| p.as_object()) {
            for (path, path_item) in paths {
                if let Some(path_item_obj) = path_item.as_object() {
                    for (method, operation) in path_item_obj {
                        if let Some(operation_obj) = operation.as_object() {
                            endpoints.push(ApiEndpoint {
                                path: path.clone(),
                                method: method.to_uppercase(),
                                operation_id: operation_obj
                                    .get("operationId")
                                    .and_then(|id| id.as_str())
                                    .map(|s| s.to_string()),
                                request_schema: self.extract_request_schema(operation_obj),
                                response_schema: self.extract_response_schema(operation_obj),
                            });
                        }
                    }
                }
            }
        }

        endpoints
    }

    fn extract_request_schema(
        &self,
        operation: &serde_json::Map<String, Value>,
    ) -> Option<SchemaReference> {
        operation
            .get("requestBody")?
            .get("content")?
            .get("application/json")?
            .get("schema")?
            .get("$ref")
            .and_then(|r| r.as_str())
            .map(|s| SchemaReference {
                name: s.to_string(),
                schema_type: crate::models::SchemaType::OpenAPI,
                location: crate::models::Location {
                    file: String::new(),
                    line: 0,
                    column: None,
                },
                metadata: std::collections::HashMap::new(),
            })
    }

    fn extract_response_schema(
        &self,
        operation: &serde_json::Map<String, Value>,
    ) -> Option<SchemaReference> {
        operation
            .get("responses")?
            .get("200")?
            .get("content")?
            .get("application/json")?
            .get("schema")?
            .get("$ref")
            .and_then(|r| r.as_str())
            .map(|s| SchemaReference {
                name: s.to_string(),
                schema_type: crate::models::SchemaType::OpenAPI,
                location: crate::models::Location {
                    file: String::new(),
                    line: 0,
                    column: None,
                },
                metadata: std::collections::HashMap::new(),
            })
    }
}

/// API эндпоинт из OpenAPI спецификации
#[derive(Debug, Clone)]
pub struct ApiEndpoint {
    pub path: String,
    pub method: String,
    pub operation_id: Option<String>,
    pub request_schema: Option<SchemaReference>,
    pub response_schema: Option<SchemaReference>,
}
