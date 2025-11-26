use crate::call_graph::{CallGraph, CallNode, Parameter};
use crate::data_flow::DataFlowTracker;
use crate::models::{
    BaseType, ChainDirection, Contract, DataChain, Link, LinkType, Location, NodeId,
    SchemaReference, SchemaType, Severity, TypeInfo,
};
use anyhow::{anyhow, bail, Result};
use std::collections::{HashMap, HashSet};
use std::path::Path;

/// Построитель цепочек данных из графа вызовов
pub struct ChainBuilder<'a> {
    /// Граф вызовов
    graph: &'a CallGraph,
    /// Отслеживатель потока данных
    #[allow(dead_code)]
    data_flow: &'a DataFlowTracker<'a>,
}

impl<'a> ChainBuilder<'a> {
    /// Создает новый построитель цепочек
    pub fn new(graph: &'a CallGraph, data_flow: &'a DataFlowTracker<'a>) -> Self {
        Self { graph, data_flow }
    }

    /// Строит цепочку от точки входа до конечной точки
    pub fn build_chain(&self, entry: NodeId, direction: ChainDirection) -> Result<DataChain> {
        match direction {
            ChainDirection::FrontendToBackend => self.build_forward_chain(entry),
            ChainDirection::BackendToFrontend => self.build_reverse_chain(entry),
        }
    }

    /// Находит все цепочки в проекте
    pub fn find_all_chains(&self) -> Result<Vec<DataChain>> {
        let mut chains = Vec::new();

        // Находим все routes (точки входа API)
        let routes =
            crate::call_graph::find_nodes(&self.graph, |n| matches!(n, CallNode::Route { .. }));

        for route in routes {
            // Строим цепочку Frontend → Backend → Database
            if let Ok(forward_chain) = self.build_forward_chain(route) {
                chains.push(forward_chain);
            }

            // Строим цепочку Database → Backend → Frontend
            if let Ok(reverse_chain) = self.build_reverse_chain(route) {
                chains.push(reverse_chain);
            }
        }

        Ok(chains)
    }

    /// Строит цепочку Frontend → Backend → Database
    pub fn build_forward_chain(&self, start: NodeId) -> Result<DataChain> {
        self.ensure_node_exists(start)?;
        let path = self.collect_path(start, |node| {
            crate::call_graph::outgoing_nodes(&self.graph, node)
        });

        if path.is_empty() {
            bail!("Не удалось построить прямую цепочку: пустой путь");
        }

        let links = self.create_links_from_nodes(&path, ChainDirection::FrontendToBackend)?;
        let contracts = self.build_contracts(&links);

        Ok(DataChain {
            id: format!("chain-{}", start.index()),
            name: self.generate_chain_name(start)?,
            links,
            contracts,
            direction: ChainDirection::FrontendToBackend,
        })
    }

    /// Строит цепочку Database → Backend → Frontend
    pub fn build_reverse_chain(&self, start: NodeId) -> Result<DataChain> {
        self.ensure_node_exists(start)?;
        let mut path = self.collect_path(start, |node| {
            crate::call_graph::incoming_nodes(&self.graph, node)
        });
        if path.is_empty() {
            bail!("Не удалось построить обратную цепочку: пустой путь");
        }
        path.reverse();

        let links = self.create_links_from_nodes(&path, ChainDirection::BackendToFrontend)?;
        let contracts = self.build_contracts(&links);

        Ok(DataChain {
            id: format!("chain-reverse-{}", start.index()),
            name: format!("{} (reverse)", self.generate_chain_name(start)?),
            links,
            contracts,
            direction: ChainDirection::BackendToFrontend,
        })
    }

    fn ensure_node_exists(&self, node_id: NodeId) -> Result<()> {
        if self.graph.node_weight(*node_id).is_some() {
            Ok(())
        } else {
            bail!("Узел {:?} отсутствует в графе", node_id);
        }
    }

    fn collect_path<F>(&self, start: NodeId, get_neighbors: F) -> Vec<NodeId>
    where
        F: Fn(NodeId) -> Vec<NodeId>,
    {
        let mut order = Vec::new();
        let mut current = start;
        let mut visited = HashSet::new();

        loop {
            if visited.contains(&current) {
                break;
            }
            visited.insert(current);
            order.push(current);

            let next = get_neighbors(current)
                .into_iter()
                .find(|candidate| !visited.contains(candidate));

            match next {
                Some(next_node) => current = next_node,
                None => break,
            }
        }

        order
    }

    fn create_links_from_nodes(
        &self,
        nodes: &[NodeId],
        _direction: ChainDirection,
    ) -> Result<Vec<Link>> {
        let total = nodes.len();
        nodes
            .iter()
            .enumerate()
            .map(|(idx, node_id)| {
                let mut link_type = self.determine_link_type(*node_id);
                // Упрощенная логика без дублирования по direction
                if total == 1 {
                    link_type = LinkType::Source;
                } else if idx == 0 {
                    link_type = LinkType::Source;
                } else if idx == total - 1 {
                    link_type = LinkType::Sink;
                }
                // Иначе используем link_type из determine_link_type
                self.create_link_from_node(*node_id, link_type)
            })
            .collect()
    }

    fn build_contracts(&self, links: &[Link]) -> Vec<Contract> {
        let mut contracts = Vec::new();
        for window in links.windows(2) {
            if let [from, to] = window {
                contracts.push(self.create_contract(from, to));
            }
        }
        contracts
    }

    fn create_contract(&self, from: &Link, to: &Link) -> Contract {
        Contract {
            from_link_id: from.id.clone(),
            to_link_id: to.id.clone(),
            from_schema: from.schema_ref.clone(),
            to_schema: to.schema_ref.clone(),
            mismatches: Vec::new(),
            severity: Severity::Info,
        }
    }

    fn create_link_from_node(&self, node_id: NodeId, link_type: LinkType) -> Result<Link> {
        let node = self
            .graph
            .node_weight(*node_id)
            .ok_or_else(|| anyhow!("Узел не найден: {:?}", node_id))?
            .clone();

        let (id, location, schema_ref) = match node {
            CallNode::Route { path, location, .. } => {
                let schema = self.extract_route_schema(node_id)?;
                (
                    format!("route-{}-{}", path.replace('/', "-"), node_id.index()),
                    location,
                    schema,
                )
            }
            CallNode::Function {
                name,
                file,
                line,
                parameters,
                ..
            } => {
                let location = self.location_from_path(&file, line);
                let schema = self.extract_function_schema(&parameters, &name, &location);
                (
                    format!("func-{}-{}", name, node_id.index()),
                    location,
                    schema,
                )
            }
            CallNode::Method {
                name,
                class,
                parameters,
                ..
            } => {
                let (file_path, line) = self.method_location(class)?;
                let location = self.location_from_path(&file_path, line);
                let schema = self.extract_function_schema(&parameters, &name, &location);
                (
                    format!("method-{}-{}", name, node_id.index()),
                    location,
                    schema,
                )
            }
            CallNode::Class { name, file, .. } => {
                let location = self.location_from_path(&file, 0);
                let schema = self.extract_class_schema(&name, &location);
                (
                    format!("class-{}-{}", name, node_id.index()),
                    location,
                    schema,
                )
            }
            CallNode::Module { path } => {
                bail!(
                    "Невозможно создать звено цепочки из модуля: {:?}",
                    path.display()
                );
            }
        };

        Ok(Link {
            id,
            link_type,
            location,
            node_id,
            schema_ref,
        })
    }

    fn extract_function_schema(
        &self,
        parameters: &[Parameter],
        fallback_name: &str,
        location: &Location,
    ) -> SchemaReference {
        for param in parameters {
            if let Some(schema) = self.schema_from_type_info(&param.type_info) {
                return schema;
            }
        }

        self.unknown_schema(fallback_name, location.clone())
    }

    fn extract_route_schema(&self, route_node_id: NodeId) -> Result<SchemaReference> {
        let route_node = self
            .graph
            .node_weight(*route_node_id)
            .ok_or_else(|| anyhow!("Route узел не найден: {:?}", route_node_id))?;

        if let CallNode::Route { handler, .. } = route_node {
            if let Some(handler_node) = self.graph.node_weight(handler.0).cloned() {
                if let CallNode::Function {
                    name,
                    parameters,
                    file,
                    line,
                    ..
                } = handler_node
                {
                    let location = self.location_from_path(&file, line);
                    return Ok(self.extract_function_schema(&parameters, &name, &location));
                }
            }
        }

        Ok(self.unknown_schema(
            "RouteRequest",
            Location {
                file: String::new(),
                line: 0,
                column: None,
            },
        ))
    }

    fn extract_class_schema(&self, name: &str, location: &Location) -> SchemaReference {
        SchemaReference {
            name: name.to_string(),
            schema_type: SchemaType::Pydantic,
            location: location.clone(),
            metadata: HashMap::new(),
        }
    }

    fn method_location(&self, class_node: NodeId) -> Result<(std::path::PathBuf, usize)> {
        let node = self
            .graph
            .node_weight(*class_node)
            .ok_or_else(|| anyhow!("Класс для метода не найден: {:?}", class_node))?;

        if let CallNode::Class { file, .. } = node {
            Ok((file.clone(), 0))
        } else {
            bail!("Узел {:?} не является классом", class_node);
        }
    }

    fn schema_from_type_info(&self, type_info: &TypeInfo) -> Option<SchemaReference> {
        if let Some(schema) = &type_info.schema_ref {
            return Some(schema.clone());
        }

        match type_info.base_type {
            BaseType::Object | BaseType::Array => {
                let mut metadata = HashMap::new();
                metadata.insert(
                    "base_type".to_string(),
                    format!("{:?}", type_info.base_type),
                );
                Some(SchemaReference {
                    name: format!("{:?}", type_info.base_type),
                    schema_type: SchemaType::JsonSchema,
                    location: Location {
                        file: String::new(),
                        line: 0,
                        column: None,
                    },
                    metadata,
                })
            }
            _ => None,
        }
    }

    fn unknown_schema(&self, name: &str, location: Location) -> SchemaReference {
        SchemaReference {
            name: name.to_string(),
            schema_type: SchemaType::JsonSchema,
            location,
            metadata: HashMap::new(),
        }
    }

    fn determine_link_type(&self, node_id: NodeId) -> LinkType {
        self.graph
            .node_weight(*node_id)
            .map(|node| match node {
                CallNode::Route { .. } => LinkType::Source,
                CallNode::Class { .. } => LinkType::Sink,
                _ => LinkType::Transformer,
            })
            .unwrap_or(LinkType::Transformer)
    }

    fn location_from_path(&self, path: &Path, line: usize) -> Location {
        Location {
            file: path.to_string_lossy().to_string(),
            line,
            column: None,
        }
    }

    fn generate_chain_name(&self, start: NodeId) -> Result<String> {
        let node = self
            .graph
            .node_weight(*start)
            .ok_or_else(|| anyhow!("Узел не найден: {:?}", start))?;

        Ok(match node {
            CallNode::Route { path, method, .. } => {
                let method_str = format!("{:?}", method).to_uppercase();
                format!("{} {}", method_str, path)
            }
            CallNode::Function { name, .. } => format!("Function {}", name),
            CallNode::Class { name, .. } => format!("Class {}", name),
            CallNode::Method { name, .. } => format!("Method {}", name),
            CallNode::Module { path } => {
                format!(
                    "Module {}",
                    path.file_name()
                        .and_then(|n| n.to_str())
                        .unwrap_or_default()
                )
            }
        })
    }
}
