use anyhow::Result;
use dc_core::models::DataChain;
use std::fs;
use std::path::Path;

/// Генератор Markdown отчетов
pub struct MarkdownReporter;

impl MarkdownReporter {
    /// Генерирует отчет в формате .chain_verification_report.md
    pub fn generate(&self, chains: &[DataChain], output_path: &str) -> Result<()> {
        let mut report = String::new();

        // Заголовок
        report.push_str("# Отчет о проверке всех цепочек данных приложения\n\n");
        report.push_str(&format!(
            "## Дата проверки\n{}\n\n",
            chrono::Utc::now().format("%Y-%m-%d")
        ));

        // Статистика - считаем цепочки, а не контракты
        let total_chains = chains.len();
        let chains_with_critical = chains
            .iter()
            .filter(|chain| {
                chain
                    .contracts
                    .iter()
                    .any(|c| c.severity == dc_core::models::Severity::Critical)
            })
            .count();
        let chains_with_warnings = chains
            .iter()
            .filter(|chain| {
                // Цепочки без Critical, но с хотя бы одним Warning
                !chain
                    .contracts
                    .iter()
                    .any(|c| c.severity == dc_core::models::Severity::Critical)
                    && chain
                        .contracts
                        .iter()
                        .any(|c| c.severity == dc_core::models::Severity::Warning)
            })
            .count();
        let valid_chains = total_chains - chains_with_critical - chains_with_warnings;

        report.push_str("## Статистика проверки\n");
        report.push_str(&format!("- **Всего цепочек**: {}\n", total_chains));
        report.push_str(&format!("- **Критические проблемы**: {}\n", chains_with_critical));
        report.push_str(&format!("- **Предупреждения**: {}\n", chains_with_warnings));
        report.push_str(&format!("- **Корректные цепочки**: {}\n\n", valid_chains));
        report.push_str("---\n\n");

        // Детали по цепочкам
        for (idx, chain) in chains.iter().enumerate() {
            report.push_str(&format!("### Цепочка {}: {}\n\n", idx + 1, chain.name));
            report.push_str(&format!("#### ID: {}\n\n", chain.id));

            // Путь данных
            report.push_str("#### Путь данных:\n```\n");
            for (idx, link) in chain.links.iter().enumerate() {
                if idx > 0 {
                    report.push_str(" → ");
                }
                report.push_str(&link.id);
            }
            report.push_str("\n```\n\n");

            // Проверенные стыки
            report.push_str("#### Проверенные стыки:\n\n");
            for (i, contract) in chain.contracts.iter().enumerate() {
                if contract.mismatches.is_empty() {
                    report.push_str(&format!(
                        "{}. ✅ **{} → {}**\n",
                        i + 1,
                        contract.from_link_id,
                        contract.to_link_id
                    ));
                    report.push_str("   - ✅ **Корректно**: все поля совпадают\n\n");
                } else {
                    report.push_str(&format!(
                        "{}. ⚠️ **{} → {}**\n",
                        i + 1,
                        contract.from_link_id,
                        contract.to_link_id
                    ));
                    for mismatch in &contract.mismatches {
                        report.push_str(&format!(
                            "   - ⚠️ **{:?}**: {}\n",
                            mismatch.mismatch_type, mismatch.message
                        ));
                    }
                    report.push_str("\n");
                }
            }

            // Результат
            let has_errors = chain.contracts.iter().any(|c| !c.mismatches.is_empty());
            if has_errors {
                report.push_str("#### Результат: ⚠️ **ТРЕБУЕТ ВНИМАНИЯ**\n\n");
            } else {
                report.push_str("#### Результат: ✅ **КОРРЕКТНА**\n\n");
            }

            report.push_str("---\n\n");
        }

        // Итоговые выводы
        report.push_str("## Итоговые выводы\n\n");
        if chains_with_critical == 0 && chains_with_warnings == 0 {
            report.push_str("### ✅ Общая оценка: **КОРРЕКТНО**\n\n");
        } else {
            report.push_str("### ⚠️ Общая оценка: **ТРЕБУЕТ ВНИМАНИЯ**\n\n");
        }

        fs::write(Path::new(output_path), report)?;
        Ok(())
    }
}
