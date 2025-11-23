use crate::config::Config;
use crate::reporters::MarkdownReporter;
use anyhow::Result;
use dc_core::analyzers::{ChainBuilder, ContractChecker};
use dc_core::data_flow::DataFlowTracker;
use dc_core::models::Severity;
use dc_adapter_fastapi::FastApiCallGraphBuilder;
use dc_typescript::TypeScriptCallGraphBuilder;
use std::path::PathBuf;

/// Выполняет проверку цепочек данных
pub fn execute_check(config_path: &str) -> Result<()> {
    // 1. Загружаем конфигурацию
    let config = Config::load(config_path)?;

    // 2. Инициализируем адаптеры и строим графы
    let mut all_chains = Vec::new();

    for adapter_config in &config.adapters {
        match adapter_config.adapter_type.as_str() {
            "fastapi" => {
                let app_path = adapter_config
                    .app_path
                    .as_ref()
                    .ok_or_else(|| anyhow::anyhow!("FastAPI adapter requires app_path"))?;
                let app_path = PathBuf::from(app_path);

                // Строим граф вызовов для FastAPI
                let builder = FastApiCallGraphBuilder::new(app_path);
                let graph = builder.build_graph()?;

                // Создаем DataFlowTracker и ChainBuilder
                let tracker = DataFlowTracker::new(&graph);
                let chain_builder = ChainBuilder::new(&graph, &tracker);

                // Находим все цепочки
                let chains = chain_builder.find_all_chains()?;
                all_chains.extend(chains);
            }
            "typescript" => {
                let src_paths = adapter_config
                    .src_paths
                    .as_ref()
                    .ok_or_else(|| anyhow::anyhow!("TypeScript adapter requires src_paths"))?;
                let src_paths: Vec<PathBuf> = src_paths.iter().map(PathBuf::from).collect();

                // Строим граф вызовов для TypeScript
                let mut builder = TypeScriptCallGraphBuilder::new(src_paths);
                let graph = builder.build_graph()?;

                // Создаем DataFlowTracker и ChainBuilder
                let tracker = DataFlowTracker::new(&graph);
                let chain_builder = ChainBuilder::new(&graph, &tracker);

                // Находим все цепочки
                let chains = chain_builder.find_all_chains()?;
                all_chains.extend(chains);
            }
            _ => {
                eprintln!("Unknown adapter type: {}", adapter_config.adapter_type);
            }
        }
    }

    // 3. Проверяем контракты на всех стыках
    let checker = ContractChecker::new();
    for chain in &mut all_chains {
        for contract in &mut chain.contracts {
            let mismatches = checker.check_contract(contract);
            contract.mismatches = mismatches.clone();

            // Определяем severity на основе типов Mismatch
            contract.severity = if mismatches
                .iter()
                .any(|m| matches!(m.mismatch_type, dc_core::models::MismatchType::TypeMismatch))
            {
                Severity::Critical
            } else if !mismatches.is_empty() {
                Severity::Warning
            } else {
                Severity::Info
            };
        }
    }

    // 4. Генерируем отчет
    let reporter = MarkdownReporter;
    reporter.generate(&all_chains, &config.output.path)?;

    println!(
        "Проверка завершена. Отчет сохранен в {}",
        config.output.path
    );

    Ok(())
}
