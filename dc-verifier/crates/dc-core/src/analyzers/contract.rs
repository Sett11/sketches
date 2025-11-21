use crate::analyzers::ContractRule;
use crate::models::{Contract, Mismatch};

/// Проверятель контрактов - применяет правила к контрактам
pub struct ContractChecker {
    rules: Vec<Box<dyn ContractRule>>,
}

impl ContractChecker {
    /// Создает новый проверятель с правилами по умолчанию
    pub fn new() -> Self {
        let mut checker = Self { rules: Vec::new() };

        // Добавляем правила по умолчанию
        checker.add_rule(Box::new(crate::analyzers::TypeMismatchRule));
        checker.add_rule(Box::new(crate::analyzers::MissingFieldRule));
        checker.add_rule(Box::new(crate::analyzers::UnnormalizedDataRule));

        checker
    }

    /// Добавляет правило проверки
    pub fn add_rule(&mut self, rule: Box<dyn ContractRule>) {
        self.rules.push(rule);
    }

    /// Проверяет контракт между двумя звеньями
    pub fn check_contract(&self, contract: &Contract) -> Vec<Mismatch> {
        let mut all_mismatches = Vec::new();

        for rule in &self.rules {
            let mismatches = rule.check(contract);
            all_mismatches.extend(mismatches);
        }

        all_mismatches
    }

    /// Сравнивает две схемы и находит несоответствия
    pub fn compare_schemas(
        &self,
        from: &crate::models::SchemaReference,
        to: &crate::models::SchemaReference,
    ) -> Vec<Mismatch> {
        // Создаем временный контракт для проверки
        let contract = Contract {
            from_link_id: String::new(),
            to_link_id: String::new(),
            from_schema: from.clone(),
            to_schema: to.clone(),
            mismatches: Vec::new(),
            severity: crate::models::Severity::Info,
        };

        // Используем все правила для проверки
        self.check_contract(&contract)
    }
}

impl Default for ContractChecker {
    fn default() -> Self {
        Self::new()
    }
}
