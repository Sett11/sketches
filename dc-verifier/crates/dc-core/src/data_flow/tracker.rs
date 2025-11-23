use crate::call_graph::CallGraph;
use crate::data_flow::{DataPath, Variable};
use crate::models::NodeId;
use std::collections::HashMap;

/// Отслеживатель потока данных через граф вызовов
pub struct DataFlowTracker<'a> {
    /// Граф вызовов
    graph: &'a CallGraph,
    /// Переменные по узлам
    variables: HashMap<NodeId, Vec<Variable>>,
}

impl<'a> DataFlowTracker<'a> {
    /// Создает новый отслеживатель
    pub fn new(graph: &'a CallGraph) -> Self {
        Self {
            graph,
            variables: HashMap::new(),
        }
    }

    /// Добавляет переменную к узлу
    pub fn add_variable(&mut self, node: NodeId, variable: Variable) {
        self.variables
            .entry(node)
            .or_insert_with(Vec::new)
            .push(variable);
    }

    /// Отслеживает переменную через граф
    pub fn track_variable(&self, var: &Variable, from: NodeId) -> Vec<DataPath> {
        let mut paths = Vec::new();

        // Находим все узлы, которые могут получить эту переменную
        let visited = &mut std::collections::HashSet::new();
        self.track_variable_recursive(var, from, &mut paths, visited);

        paths
    }

    fn track_variable_recursive(
        &self,
        var: &Variable,
        current: NodeId,
        paths: &mut Vec<DataPath>,
        visited: &mut std::collections::HashSet<NodeId>,
    ) {
        if visited.contains(&current) {
            return;
        }
        visited.insert(current);

        // Идем по исходящим ребрам (вызовам)
        for neighbor in crate::call_graph::outgoing_nodes(self.graph, current) {
            // Проверяем, используется ли переменная в этом узле
            if let Some(vars) = self.variables.get(&neighbor) {
                for v in vars {
                    if v.name == var.name {
                        let mut path = DataPath::new(current, neighbor, var.clone());
                        path.push_node(current);
                        paths.push(path);
                    }
                }
            }

            // Рекурсивно продолжаем отслеживание
            self.track_variable_recursive(var, neighbor, paths, visited);
        }
    }

    /// Отслеживает параметр функции через вызовы
    pub fn track_parameter(&self, param_name: &str, func: NodeId) -> Vec<DataPath> {
        let mut paths = Vec::new();
        let visited = &mut std::collections::HashSet::new();

        // Создаем переменную для параметра
        let param_var = Self::create_param_variable(param_name);

        // Находим все узлы, которые вызывают эту функцию
        let callers = crate::call_graph::incoming_nodes(self.graph, func);
        
        for caller in callers {
            // Проверяем, передается ли параметр через вызов
            if let Some(edge) = self.graph.edges_connecting(*caller, *func).next() {
                if let crate::call_graph::CallEdge::Call { argument_mapping, .. } = edge.weight() {
                    // Ищем параметр в маппинге аргументов
                    for (param, var_name) in argument_mapping {
                        if param == param_name || var_name == param_name {
                            let mut path = DataPath::new(caller, func, param_var.clone());
                            path.push_node(caller);
                            paths.push(path);
                            
                            // Рекурсивно отслеживаем дальше
                            self.track_parameter_recursive(
                                param_name,
                                func,
                                &mut paths,
                                visited,
                            );
                        }
                    }
                }
            }
        }

        paths
    }

    fn track_parameter_recursive(
        &self,
        param_name: &str,
        current: NodeId,
        paths: &mut Vec<DataPath>,
        visited: &mut std::collections::HashSet<NodeId>,
    ) {
        if visited.contains(&current) {
            return;
        }
        visited.insert(current);

        // Идем по исходящим ребрам (вызовам из этой функции)
        for neighbor in crate::call_graph::outgoing_nodes(self.graph, current) {
            // Проверяем, используется ли параметр в вызове
            if let Some(edge) = self.graph.edges_connecting(*current, *neighbor).next() {
                if let crate::call_graph::CallEdge::Call { argument_mapping, .. } = edge.weight() {
                    for (_param, var_name) in argument_mapping {
                        if var_name == param_name {
                            let param_var = Self::create_param_variable(param_name);
                            let mut path = DataPath::new(current, neighbor, param_var);
                            path.push_node(current);
                            paths.push(path);
                        }
                    }
                }
            }

            // Рекурсивно продолжаем
            self.track_parameter_recursive(param_name, neighbor, paths, visited);
        }
    }

    /// Отслеживает возвращаемое значение
    pub fn track_return(&self, func: NodeId) -> Vec<DataPath> {
        let mut paths = Vec::new();
        let mut visited = std::collections::HashSet::new();

        // Создаем переменную для возвращаемого значения
        let return_var = Self::create_return_variable();

        // Находим все узлы, которые вызывают эту функцию
        let callers = crate::call_graph::incoming_nodes(self.graph, func);
        
        for caller in callers {
            // Создаем путь от функции к вызывающему узлу
            let mut path = DataPath::new(func, caller, return_var.clone());
            path.push_node(func);
            paths.push(path);
        }

        // Также отслеживаем использование возвращаемого значения дальше
        self.track_return_recursive(func, &mut paths, &mut visited);

        paths
    }

    fn track_return_recursive(
        &self,
        current: NodeId,
        paths: &mut Vec<DataPath>,
        visited: &mut std::collections::HashSet<NodeId>,
    ) {
        if visited.contains(&current) {
            return;
        }
        visited.insert(current);

        // Идем по входящим ребрам (кто вызывает эту функцию)
        for caller in crate::call_graph::incoming_nodes(self.graph, current) {
            // Идем по исходящим ребрам вызывающего узла (куда передается возвращаемое значение)
            for next_node in crate::call_graph::outgoing_nodes(self.graph, caller) {
                if next_node != current {
                    let return_var = Self::create_return_variable();
                    let mut path = DataPath::new(caller, next_node, return_var);
                    path.push_node(caller);
                    paths.push(path);
                }
            }
        }

        // Рекурсивно продолжаем для всех узлов, которые вызывают эту функцию
        for caller in crate::call_graph::incoming_nodes(self.graph, current) {
            self.track_return_recursive(caller, paths, visited);
        }
    }

    /// Создает переменную для параметра
    fn create_param_variable(param_name: &str) -> Variable {
        Variable {
            name: param_name.to_string(),
            type_info: crate::models::TypeInfo {
                base_type: crate::models::BaseType::Unknown,
                schema_ref: None,
                constraints: Vec::new(),
                optional: false,
            },
            location: crate::models::Location {
                file: String::new(),
                line: 0,
                column: None,
            },
            source: crate::data_flow::VariableSource::Parameter,
        }
    }

    /// Создает переменную для возвращаемого значения
    fn create_return_variable() -> Variable {
        Variable {
            name: "return".to_string(),
            type_info: crate::models::TypeInfo {
                base_type: crate::models::BaseType::Unknown,
                schema_ref: None,
                constraints: Vec::new(),
                optional: false,
            },
            location: crate::models::Location {
                file: String::new(),
                line: 0,
                column: None,
            },
            source: crate::data_flow::VariableSource::Return,
        }
    }
}
