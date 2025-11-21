use anyhow::{Context, Result};
use rustpython_parser::{ast, parse, Mode};
use std::collections::{HashMap, HashSet};
use std::fs;
use std::path::{Path, PathBuf};

use crate::call_graph::{CallEdge, CallGraph, CallNode, HttpMethod, Parameter};
use crate::call_graph::decorator::Decorator;
use crate::models::{BaseType, Location, NodeId, TypeInfo};
use crate::parsers::{Call, Import, PythonParser};

/// Построитель графа вызовов - главный класс для создания графа из кода
pub struct CallGraphBuilder {
    /// Граф вызовов
    graph: CallGraph,
    /// Точки входа в приложение
    entry_points: Vec<PathBuf>,
    /// Обработанные файлы (для избежания циклов)
    processed_files: HashSet<PathBuf>,
    /// Парсер исходников
    parser: PythonParser,
    /// Кэш узлов-модулей
    module_nodes: HashMap<PathBuf, NodeId>,
    /// Кэш функций/методов (ключ: файл + имя)
    function_nodes: HashMap<String, NodeId>,
    /// Корень проекта
    project_root: Option<PathBuf>,
}

impl CallGraphBuilder {
    /// Создает новый построитель графа
    pub fn new() -> Self {
        Self::with_parser(PythonParser::new())
    }

    /// Создает построитель графа с кастомным парсером (для тестов)
    pub fn with_parser(parser: PythonParser) -> Self {
        Self {
            graph: CallGraph::new(),
            entry_points: Vec::new(),
            processed_files: HashSet::new(),
            parser,
            module_nodes: HashMap::new(),
            function_nodes: HashMap::new(),
            project_root: None,
        }
    }

    /// Находит точку входа (main.py, app.py) в проекте
    pub fn find_entry_point(&self, project_root: &Path) -> Result<PathBuf> {
        let candidates = ["main.py", "app.py", "__main__.py"];

        for candidate in &candidates {
            let path = project_root.join(candidate);
            if path.exists() {
                return Ok(path);
            }
        }

        anyhow::bail!("Entry point not found in {:?}", project_root)
    }

    /// Строит граф от точки входа
    pub fn build_from_entry(&mut self, entry: &Path) -> Result<()> {
        let normalized_entry = Self::normalize_path(entry);

        if self.processed_files.contains(&normalized_entry) {
            return Ok(()); // Уже обработан
        }

        if self.project_root.is_none() {
            if let Some(parent) = normalized_entry.parent() {
                self.project_root = Some(parent.to_path_buf());
            }
        }

        let source = fs::read_to_string(&normalized_entry)
            .with_context(|| format!("Failed to read {:?}", normalized_entry))?;
        let ast = parse(
            &source,
            Mode::Module,
            normalized_entry.to_string_lossy().as_ref(),
        )
        .with_context(|| format!("Failed to parse {:?}", normalized_entry))?;

        let module_node = self.get_or_create_module_node(&normalized_entry)?;

        self.processed_files.insert(normalized_entry.clone());
        self.entry_points.push(normalized_entry.clone());

        self.process_imports(&ast, module_node, &normalized_entry)?;
        self.extract_functions_and_classes(&ast, &normalized_entry)?;
        self.process_calls(&ast, module_node, &normalized_entry)?;
        self.process_decorators(&ast, &normalized_entry)?;

        Ok(())
    }

    /// Обрабатывает импорт: добавляет узел и ребро
    pub fn process_import(
        &mut self,
        from: NodeId,
        import: &Import,
        current_file: &Path,
    ) -> Result<NodeId> {
        let import_path = match self.resolve_import_path(&import.path, current_file) {
            Ok(path) => path,
            Err(err) => {
                eprintln!(
                    "Не удалось разрешить импорт '{}' из {:?}: {}",
                    import.path, current_file, err
                );
                return Ok(from);
            }
        };
        let module_node = self.get_or_create_module_node(&import_path)?;

        self.graph.add_edge(
            *from,
            *module_node,
            CallEdge::Import {
                from,
                to: module_node,
                import_path: import.path.clone(),
                file: import_path.clone(),
            },
        );

        // Рекурсивно строим граф для импортированного модуля
        let _ = self.build_from_entry(&import_path);

        Ok(module_node)
    }

    /// Обрабатывает вызов функции: добавляет ребро
    pub fn process_call(
        &mut self,
        caller: NodeId,
        call: &Call,
        current_file: &Path,
    ) -> Result<NodeId> {
        let Some(callee_node) = self.find_function_node(&call.name, current_file) else {
            // TODO: добавить логгирование после интеграции с tracing
            return Ok(caller);
        };

        let argument_mapping = call
            .arguments
            .iter()
            .enumerate()
            .map(|(idx, arg)| {
                let key = arg
                    .parameter_name
                    .clone()
                    .unwrap_or_else(|| format!("arg{}", idx));
                (key, arg.value.clone())
            })
            .collect();

        self.graph.add_edge(
            *caller,
            *callee_node,
            CallEdge::Call {
                caller,
                callee: callee_node,
                argument_mapping,
                location: call.location.clone(),
            },
        );

        if let Some(file) = self.node_file_path(callee_node) {
            let normalized = Self::normalize_path(&file);
            if !self.processed_files.contains(&normalized) {
                let _ = self.build_from_entry(&normalized);
            }
        }

        Ok(callee_node)
    }

    /// Обрабатывает декоратор FastAPI (@app.post)
    pub fn process_decorator(&mut self, decorator: &Decorator, current_file: &Path) -> Result<()> {
        if !self.is_route_decorator(&decorator.name) {
            return Ok(());
        }

        let handler_name = match &decorator.target_function {
            Some(name) => name,
            None => return Ok(()),
        };

        let Some(handler_node) = self.find_function_node(handler_name, current_file) else {
            return Ok(());
        };

        let http_method = self
            .extract_http_method(&decorator.name)
            .unwrap_or(HttpMethod::Get);
        let route_path = decorator
            .arguments
            .first()
            .cloned()
            .unwrap_or_else(|| "/".to_string());

        let mut location = decorator.location.clone();
        if location.file.is_empty() {
            location.file = current_file.to_string_lossy().to_string();
        }

        let route_node = NodeId::from(self.graph.add_node(CallNode::Route {
            path: route_path,
            method: http_method,
            handler: handler_node,
            location: location.clone(),
        }));

        self.graph.add_edge(
            route_node.0,
            handler_node.0,
            CallEdge::Call {
                caller: route_node,
                callee: handler_node,
                argument_mapping: Vec::new(),
                location,
            },
        );

        Ok(())
    }

    /// Получает построенный граф
    pub fn into_graph(self) -> CallGraph {
        self.graph
    }

    /// Получает ссылку на граф
    pub fn graph(&self) -> &CallGraph {
        &self.graph
    }

    /// Получает мутабельную ссылку на граф
    pub fn graph_mut(&mut self) -> &mut CallGraph {
        &mut self.graph
    }
}

impl Default for CallGraphBuilder {
    fn default() -> Self {
        Self::new()
    }
}

impl CallGraphBuilder {
    fn process_imports(
        &mut self,
        module_ast: &ast::Mod,
        module_node: NodeId,
        file_path: &Path,
    ) -> Result<()> {
        let file_path_str = file_path.to_string_lossy().to_string();
        let imports = self.parser.extract_imports(module_ast, &file_path_str);
        for import in imports {
            if let Err(err) = self.process_import(module_node, &import, file_path) {
                eprintln!(
                    "Не удалось обработать импорт {} в {:?}: {}",
                    import.path, file_path, err
                );
            }
        }
        Ok(())
    }

    fn extract_functions_and_classes(
        &mut self,
        module_ast: &ast::Mod,
        file_path: &Path,
    ) -> Result<()> {
        if let ast::Mod::Module(module) = module_ast {
            for stmt in &module.body {
                self.handle_definition(stmt, file_path, None)?;
            }
        }
        Ok(())
    }

    fn handle_definition(
        &mut self,
        stmt: &ast::Stmt,
        file_path: &Path,
        class_context: Option<(String, NodeId)>,
    ) -> Result<()> {
        match stmt {
            ast::Stmt::FunctionDef(func_def) => {
                if let Some((class_name, class_node)) = class_context {
                    let method_id =
                        self.add_method_node(&class_name, class_node, func_def, file_path)?;
                    if let Some(CallNode::Class { methods, .. }) =
                        self.graph.node_weight_mut(*class_node)
                    {
                        if !methods.contains(&method_id) {
                            methods.push(method_id);
                        }
                    }
                } else {
                    self.add_function_node(func_def, file_path)?;
                }
            }
            ast::Stmt::AsyncFunctionDef(func_def) => {
                if let Some((class_name, class_node)) = class_context {
                    let method_id =
                        self.add_async_method_node(&class_name, class_node, func_def, file_path)?;
                    if let Some(CallNode::Class { methods, .. }) =
                        self.graph.node_weight_mut(*class_node)
                    {
                        if !methods.contains(&method_id) {
                            methods.push(method_id);
                        }
                    }
                } else {
                    self.add_async_function_node(func_def, file_path)?;
                }
            }
            ast::Stmt::ClassDef(class_def) => {
                let class_node = self.add_class_node(class_def, file_path)?;
                let class_name = class_def.name.to_string();
                for body_stmt in &class_def.body {
                    self.handle_definition(
                        body_stmt,
                        file_path,
                        Some((class_name.clone(), class_node)),
                    )?;
                }
            }
            _ => {}
        }
        Ok(())
    }

    fn add_function_node(
        &mut self,
        func_def: &ast::StmtFunctionDef,
        file_path: &Path,
    ) -> Result<NodeId> {
        let parameters = self.convert_parameters(&func_def.args);

        let node_id = NodeId::from(self.graph.add_node(CallNode::Function {
            name: func_def.name.to_string(),
            file: file_path.to_path_buf(),
            line: 0, // TODO: получить location из stmt
            parameters,
            return_type: None,
        }));

        let key = Self::function_key(file_path, &func_def.name);
        self.function_nodes.insert(key, node_id);

        Ok(node_id)
    }

    fn add_async_function_node(
        &mut self,
        func_def: &ast::StmtAsyncFunctionDef,
        file_path: &Path,
    ) -> Result<NodeId> {
        let parameters = self.convert_parameters(&func_def.args);

        let node_id = NodeId::from(self.graph.add_node(CallNode::Function {
            name: func_def.name.to_string(),
            file: file_path.to_path_buf(),
            line: 0, // TODO: получить location из stmt
            parameters,
            return_type: None,
        }));

        let key = Self::function_key(file_path, &func_def.name);
        self.function_nodes.insert(key, node_id);

        Ok(node_id)
    }

    fn add_method_node(
        &mut self,
        class_name: &str,
        class_node: NodeId,
        func_def: &ast::StmtFunctionDef,
        file_path: &Path,
    ) -> Result<NodeId> {
        let mut parameters = self.convert_parameters(&func_def.args);
        if !parameters.is_empty() {
            // Удаляем self
            parameters.remove(0);
        }

        let node_id = NodeId::from(self.graph.add_node(CallNode::Method {
            name: func_def.name.to_string(),
            class: class_node,
            parameters,
            return_type: None,
        }));

        let key = Self::function_key(file_path, &format!("{}.{}", class_name, func_def.name));
        self.function_nodes.insert(key, node_id);

        Ok(node_id)
    }

    fn add_async_method_node(
        &mut self,
        class_name: &str,
        class_node: NodeId,
        func_def: &ast::StmtAsyncFunctionDef,
        file_path: &Path,
    ) -> Result<NodeId> {
        let mut parameters = self.convert_parameters(&func_def.args);
        if !parameters.is_empty() {
            parameters.remove(0);
        }

        let node_id = NodeId::from(self.graph.add_node(CallNode::Method {
            name: func_def.name.to_string(),
            class: class_node,
            parameters,
            return_type: None,
        }));

        let key = Self::function_key(file_path, &format!("{}.{}", class_name, func_def.name));
        self.function_nodes.insert(key, node_id);

        Ok(node_id)
    }

    fn add_class_node(
        &mut self,
        class_def: &ast::StmtClassDef,
        file_path: &Path,
    ) -> Result<NodeId> {
        let node_id = NodeId::from(self.graph.add_node(CallNode::Class {
            name: class_def.name.to_string(),
            file: file_path.to_path_buf(),
            methods: Vec::new(),
        }));

        let key = Self::function_key(file_path, &class_def.name);
        self.function_nodes.insert(key, node_id);

        Ok(node_id)
    }

    fn process_calls(
        &mut self,
        module_ast: &ast::Mod,
        module_node: NodeId,
        file_path: &Path,
    ) -> Result<()> {
        let file_path_str = file_path.to_string_lossy().to_string();
        let calls = self.parser.extract_calls(module_ast, &file_path_str);
        for call in calls {

            let caller_node = match &call.caller {
                Some(caller_name) => self.find_function_node(caller_name, file_path),
                None => Some(module_node),
            };

            if let Some(caller) = caller_node {
                if let Err(err) = self.process_call(caller, call, file_path) {
                    eprintln!(
                        "Не удалось обработать вызов {} в {:?}: {}",
                        call.name, file_path, err
                    );
                }
            }
        }
        Ok(())
    }

    fn process_decorators(&mut self, module_ast: &ast::Mod, file_path: &Path) -> Result<()> {
        let file_path_str = file_path.to_string_lossy().to_string();
        let decorators = self.parser.extract_decorators(module_ast, &file_path_str);
        for decorator in decorators {
            if let Err(err) = self.process_decorator(decorator, file_path) {
                eprintln!(
                    "Не удалось обработать декоратор {} в {:?}: {}",
                    decorator.name, file_path, err
                );
            }
        }
        Ok(())
    }

    fn convert_parameters(&self, args: &ast::Arguments) -> Vec<Parameter> {
        let mut params = Vec::new();
        for arg in &args.posonlyargs {
            params.push(self.create_parameter(arg));
        }
        for arg in &args.args {
            params.push(self.create_parameter(arg));
        }
        for arg in &args.kwonlyargs {
            params.push(self.create_parameter(arg));
        }
        if let Some(arg) = &args.vararg {
            params.push(self.create_parameter(arg));
        }
        if let Some(arg) = &args.kwarg {
            params.push(self.create_parameter(arg));
        }
        params
    }

    fn create_parameter(&self, arg: &ast::ArgWithDefault) -> Parameter {
        Parameter {
            name: arg.def.arg.to_string(),
            type_info: TypeInfo {
                base_type: BaseType::Unknown,
                schema_ref: None,
                constraints: Vec::new(),
                optional: arg.def.annotation.is_none(),
            },
            optional: arg.def.annotation.is_none(),
            default_value: arg.default.as_ref().map(|_| "default".to_string()),
        }
    }

    fn get_or_create_module_node(&mut self, path: &Path) -> Result<NodeId> {
        let normalized = Self::normalize_path(path);
        if let Some(node) = self.module_nodes.get(&normalized) {
            return Ok(*node);
        }

        let node = NodeId::from(self.graph.add_node(CallNode::Module {
            path: normalized.clone(),
        }));
        self.module_nodes.insert(normalized, node);
        Ok(node)
    }

    fn function_key(path: &Path, name: &str) -> String {
        format!("{}::{}", Self::normalize_path(path).to_string_lossy(), name)
    }

    fn find_function_node(&self, name: &str, current_file: &Path) -> Option<NodeId> {
        let normalized = Self::normalize_path(current_file);
        let direct_key = Self::function_key(&normalized, name);
        if let Some(node) = self.function_nodes.get(&direct_key) {
            return Some(*node);
        }

        if let Some((_, node)) = self
            .function_nodes
            .iter()
            .find(|(key, _)| key.ends_with(&format!("::{}", name)))
        {
            return Some(*node);
        }

        crate::call_graph::find_node_by_name(&self.graph, name)
    }

    fn node_file_path(&self, node_id: NodeId) -> Option<PathBuf> {
        let node = self.graph.node_weight(*node_id)?.clone();
        match node {
            CallNode::Function { file, .. } => Some(file),
            CallNode::Class { file, .. } => Some(file),
            CallNode::Module { path } => Some(path),
            CallNode::Method { class, .. } => {
                self.graph.node_weight(*class).and_then(|owner| match owner {
                    CallNode::Class { file, .. } => Some(file.clone()),
                    _ => None,
                })
            }
            CallNode::Route { location, .. } => {
                if location.file.is_empty() {
                    None
                } else {
                    Some(PathBuf::from(location.file))
                }
            }
        }
    }

    fn resolve_import_path(&self, import_path: &str, current_file: &Path) -> Result<PathBuf> {
        let normalized_current = Self::normalize_path(current_file);
        let base_dir = normalized_current
            .parent()
            .map(|p| p.to_path_buf())
            .or_else(|| self.project_root.clone())
            .unwrap_or_else(|| PathBuf::from("."));

        let candidate = if import_path.starts_with('.') {
            self.resolve_relative_import(import_path, &base_dir)
        } else {
            self.resolve_absolute_import(import_path)
        };

        if candidate.exists() {
            return Ok(candidate);
        }

        // Пробуем добавить .py, если файл не найден
        if candidate.extension().is_none() {
            let mut with_ext = candidate.clone();
            with_ext.set_extension("py");
            if with_ext.exists() {
                return Ok(with_ext);
            }
        }

        anyhow::bail!(
            "Cannot resolve import path {} from {:?}",
            import_path,
            current_file
        )
    }

    fn resolve_relative_import(&self, import_path: &str, base_dir: &Path) -> PathBuf {
        let mut level = 0;
        for ch in import_path.chars() {
            if ch == '.' {
                level += 1;
            } else {
                break;
            }
        }

        let mut path = base_dir.to_path_buf();
        for _ in 1..level {
            if let Some(parent) = path.parent() {
                path = parent.to_path_buf();
            }
        }

        let remaining = import_path.trim_start_matches('.');
        if !remaining.is_empty() {
            let replaced = remaining.replace('.', &std::path::MAIN_SEPARATOR.to_string());
            path = path.join(replaced);
        }

        if path.is_dir() {
            path.join("__init__.py")
        } else if path.extension().is_none() {
            let mut with_ext = path.clone();
            with_ext.set_extension("py");
            with_ext
        } else {
            path
        }
    }

    fn resolve_absolute_import(&self, import_path: &str) -> PathBuf {
        let root = self
            .project_root
            .clone()
            .unwrap_or_else(|| PathBuf::from("."));
        let replaced = import_path.replace('.', &std::path::MAIN_SEPARATOR.to_string());
        let mut path = root.join(replaced);

        if path.is_dir() {
            path = path.join("__init__.py");
        } else if path.extension().is_none() {
            path.set_extension("py");
        }
        path
    }

    fn normalize_path(path: &Path) -> PathBuf {
        path.canonicalize().unwrap_or_else(|_| path.to_path_buf())
    }

    fn is_route_decorator(&self, name: &str) -> bool {
        name.starts_with("app.") || name.starts_with("router.") || name.contains(".route")
    }

    fn extract_http_method(&self, decorator_name: &str) -> Option<HttpMethod> {
        let method_part = decorator_name.split('.').nth(1)?;
        HttpMethod::from_str(method_part)
    }
}
