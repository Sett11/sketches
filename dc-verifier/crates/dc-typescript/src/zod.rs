use dc_core::models::{Location, SchemaReference, SchemaType};
use swc_ecma_ast::{CallExpr, Callee, Expr, MemberProp};

/// Извлекатель Zod схем из TypeScript кода
pub struct ZodExtractor;

impl ZodExtractor {
    /// Создает новый экстрактор
    pub fn new() -> Self {
        Self
    }

    /// Извлекает Zod схему из AST узла
    pub fn extract_schema(
        &self,
        node: &Expr,
        file_path: &str,
        line: usize,
    ) -> Option<SchemaReference> {
        // Ищем вызовы z.object(), z.string(), и т.д.
        if let Expr::Call(call_expr) = node {
            if let Callee::Expr(callee_expr) = &call_expr.callee {
                // Проверяем, является ли это вызовом z.object() или подобным
                if self.is_zod_call(callee_expr) {
                    // Извлекаем имя схемы из контекста или создаем дефолтное
                    let schema_name = self.extract_schema_name(call_expr, None);

                    return Some(SchemaReference {
                        name: schema_name,
                        schema_type: SchemaType::Zod,
                        location: Location {
                            file: file_path.to_string(),
                            line,
                            column: None,
                        },
                        metadata: std::collections::HashMap::new(),
                    });
                }
            }
        }
        None
    }

    /// Извлекает Zod схему из AST узла с контекстом (для использования из TypeScriptParser)
    pub fn extract_schema_with_context(
        &self,
        call_expr: &CallExpr,
        var_name: Option<&str>,
        file_path: &str,
        line: usize,
    ) -> Option<SchemaReference> {
        if let Callee::Expr(callee_expr) = &call_expr.callee {
            if self.is_zod_call(callee_expr) {
                let schema_name = self.extract_schema_name(call_expr, var_name);

                return Some(SchemaReference {
                    name: schema_name,
                    schema_type: SchemaType::Zod,
                    location: Location {
                        file: file_path.to_string(),
                        line,
                        column: None,
                    },
                    metadata: std::collections::HashMap::new(),
                });
            }
        }
        None
    }

    /// Проверяет, является ли выражение вызовом Zod (z.object, z.string и т.д.)
    fn is_zod_call(&self, expr: &Expr) -> bool {
        match expr {
            Expr::Member(member_expr) => {
                if let Expr::Ident(ident) = member_expr.obj.as_ref() {
                    if ident.sym.as_ref() == "z" {
                        // Проверяем методы Zod
                        if let MemberProp::Ident(prop) = &member_expr.prop {
                            let method = prop.sym.as_ref();
                            return method == "object"
                                || method == "string"
                                || method == "number"
                                || method == "boolean"
                                || method == "array";
                        }
                    }
                }
            }
            _ => {}
        }
        false
    }

    /// Извлекает имя схемы из вызова
    fn extract_schema_name(&self, _call_expr: &CallExpr, var_name: Option<&str>) -> String {
        // Используем имя переменной, если оно передано
        if let Some(name) = var_name {
            return name.to_string();
        }

        // Пытаемся найти имя переменной из контекста
        // Пока возвращаем дефолтное имя, если контекст недоступен
        "ZodSchema".to_string()
    }

    /// Преобразует Zod схему в SchemaReference
    pub fn zod_to_schema(&self, zod_schema: &str, location: Location) -> SchemaReference {
        SchemaReference {
            name: zod_schema.to_string(),
            schema_type: SchemaType::Zod,
            location,
            metadata: std::collections::HashMap::new(),
        }
    }
}

impl Default for ZodExtractor {
    fn default() -> Self {
        Self::new()
    }
}
