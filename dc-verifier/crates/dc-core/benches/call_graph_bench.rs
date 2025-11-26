use criterion::{black_box, criterion_group, criterion_main, Criterion};
use dc_core::call_graph::{CallGraph, CallNode};
use dc_core::models::NodeId;

fn build_trivial_graph() -> CallGraph {
    let mut graph = CallGraph::default();
    // Сначала создаем handler node
    let handler = NodeId::from(graph.add_node(CallNode::Function {
        name: "health_check".into(),
        file: std::path::PathBuf::from("app/routes/health.py"),
        line: 1,
        parameters: Vec::new(),
        return_type: None,
    }));
    // Затем создаем Route node с уже созданным handler
    let route = graph.add_node(CallNode::Route {
        path: "/health".into(),
        method: dc_core::call_graph::HttpMethod::Get,
        handler,
        location: dc_core::models::Location {
            file: "app/routes/health.py".into(),
            line: 1,
            column: None,
        },
    });
    // Обратное ребро не требуется, но мы возвращаем индекс,
    // чтобы бенчмарку было что измерять.
    black_box(route);
    graph
}

fn bench_call_graph_building(c: &mut Criterion) {
    c.bench_function("call_graph_trivial_build", |b| {
        b.iter(|| {
            black_box(build_trivial_graph());
        });
    });
}

criterion_group!(benches, bench_call_graph_building);
criterion_main!(benches);
