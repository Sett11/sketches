use crate::analyzers::schema_parser::{FieldInfo, JsonSchema, SchemaParser};
use crate::models::{BaseType, Contract, Location, Mismatch, MismatchType, TypeInfo};

/// Трейт для правил проверки контрактов
pub trait ContractRule: Send + Sync {
    /// Проверяет контракт и возвращает найденные несоответствия
    fn check(&self, contract: &Contract) -> Vec<Mismatch>;

    /// Имя правила
    fn name(&self) -> &str;
}

/// Правило проверки несоответствия типов
pub struct TypeMismatchRule;

impl ContractRule for TypeMismatchRule {
    fn check(&self, contract: &Contract) -> Vec<Mismatch> {
        let mut mismatches = Vec::new();

        // Парсим схемы
        let Ok(from_schema) = SchemaParser::parse(&contract.from_schema) else {
            return mismatches;
        };
        let Ok(to_schema) = SchemaParser::parse(&contract.to_schema) else {
            return mismatches;
        };

        // Сравниваем типы полей
        for (field_name, from_field) in &from_schema.properties {
            if let Some(to_field) = to_schema.properties.get(field_name) {
                // Проверяем несоответствие типов
                if from_field.base_type != to_field.base_type {
                    mismatches.push(Mismatch {
                        mismatch_type: MismatchType::TypeMismatch,
                        path: field_name.clone(),
                        expected: TypeInfo {
                            base_type: from_field.base_type,
                            schema_ref: None,
                            constraints: from_field.constraints.clone(),
                            optional: from_field.optional,
                        },
                        actual: TypeInfo {
                            base_type: to_field.base_type,
                            schema_ref: None,
                            constraints: to_field.constraints.clone(),
                            optional: to_field.optional,
                        },
                        location: contract.to_schema.location.clone(),
                        message: format!(
                            "Type mismatch for field '{}': expected {:?}, got {:?}",
                            field_name, from_field.base_type, to_field.base_type
                        ),
                    });
                }
            }
        }

        mismatches
    }

    fn name(&self) -> &str {
        "type_mismatch"
    }
}

/// Правило проверки отсутствующих полей
pub struct MissingFieldRule;

impl ContractRule for MissingFieldRule {
    fn check(&self, contract: &Contract) -> Vec<Mismatch> {
        let mut mismatches = Vec::new();

        // Парсим схемы
        let Ok(from_schema) = SchemaParser::parse(&contract.from_schema) else {
            return mismatches;
        };
        let Ok(to_schema) = SchemaParser::parse(&contract.to_schema) else {
            return mismatches;
        };

        // Проверяем обязательные поля в схеме приемника
        for required_field in &to_schema.required {
            if !from_schema.properties.contains_key(required_field) {
                // Поле отсутствует в схеме источника
                let to_field = to_schema.properties.get(required_field);
                mismatches.push(Mismatch {
                    mismatch_type: MismatchType::MissingField,
                    path: required_field.clone(),
                    expected: TypeInfo {
                        base_type: to_field
                            .map(|f| f.base_type)
                            .unwrap_or(BaseType::Unknown),
                        schema_ref: None,
                        constraints: to_field
                            .map(|f| f.constraints.clone())
                            .unwrap_or_default(),
                        optional: false, // Обязательное поле
                    },
                    actual: TypeInfo {
                        base_type: BaseType::Unknown,
                        schema_ref: None,
                        constraints: Vec::new(),
                        optional: true,
                    },
                    location: contract.from_schema.location.clone(),
                    message: format!(
                        "Missing required field '{}' in source schema",
                        required_field
                    ),
                });
            }
        }

        // Также проверяем поля, которые есть в to_schema, но отсутствуют в from_schema
        // (если они не опциональные)
        for (field_name, to_field) in &to_schema.properties {
            if !to_field.optional && !from_schema.properties.contains_key(field_name) {
                if !to_schema.required.contains(field_name) {
                    // Добавляем в required, если еще не там
                    mismatches.push(Mismatch {
                        mismatch_type: MismatchType::MissingField,
                        path: field_name.clone(),
                        expected: TypeInfo {
                            base_type: to_field.base_type,
                            schema_ref: None,
                            constraints: to_field.constraints.clone(),
                            optional: false,
                        },
                        actual: TypeInfo {
                            base_type: BaseType::Unknown,
                            schema_ref: None,
                            constraints: Vec::new(),
                            optional: true,
                        },
                        location: contract.from_schema.location.clone(),
                        message: format!(
                            "Missing required field '{}' in source schema",
                            field_name
                        ),
                    });
                }
            }
        }

        mismatches
    }

    fn name(&self) -> &str {
        "missing_field"
    }
}

/// Правило проверки ненормализованных данных
pub struct UnnormalizedDataRule;

impl ContractRule for UnnormalizedDataRule {
    fn check(&self, contract: &Contract) -> Vec<Mismatch> {
        let mut mismatches = Vec::new();

        // Парсим схемы
        let Ok(from_schema) = SchemaParser::parse(&contract.from_schema) else {
            return mismatches;
        };
        let Ok(to_schema) = SchemaParser::parse(&contract.to_schema) else {
            return mismatches;
        };

        // Проверяем поля, которые требуют нормализации
        for (field_name, from_field) in &from_schema.properties {
            if let Some(to_field) = to_schema.properties.get(field_name) {
                // Проверяем ограничения на нормализацию
                let from_has_email = from_field
                    .constraints
                    .iter()
                    .any(|c| matches!(c, crate::models::Constraint::Email));
                let to_has_email = to_field
                    .constraints
                    .iter()
                    .any(|c| matches!(c, crate::models::Constraint::Email));

                // Если в приемнике требуется email, но в источнике нет валидации email
                // или наоборот - это может быть проблемой нормализации
                if to_has_email && !from_has_email && from_field.base_type == BaseType::String {
                    mismatches.push(Mismatch {
                        mismatch_type: MismatchType::UnnormalizedData,
                        path: field_name.clone(),
                        expected: TypeInfo {
                            base_type: to_field.base_type,
                            schema_ref: None,
                            constraints: to_field.constraints.clone(),
                            optional: to_field.optional,
                        },
                        actual: TypeInfo {
                            base_type: from_field.base_type,
                            schema_ref: None,
                            constraints: from_field.constraints.clone(),
                            optional: from_field.optional,
                        },
                        location: contract.from_schema.location.clone(),
                        message: format!(
                            "Field '{}' may require normalization (email format expected)",
                            field_name
                        ),
                    });
                }

                // Проверяем другие ограничения, которые могут требовать нормализации
                // Например, строки должны быть в нижнем регистре
                let to_has_pattern = to_field
                    .constraints
                    .iter()
                    .any(|c| matches!(c, crate::models::Constraint::Pattern(_)));
                if to_has_pattern && !from_has_email && from_field.base_type == BaseType::String {
                    // Если в приемнике есть паттерн, но в источнике нет - возможна проблема
                    mismatches.push(Mismatch {
                        mismatch_type: MismatchType::UnnormalizedData,
                        path: field_name.clone(),
                        expected: TypeInfo {
                            base_type: to_field.base_type,
                            schema_ref: None,
                            constraints: to_field.constraints.clone(),
                            optional: to_field.optional,
                        },
                        actual: TypeInfo {
                            base_type: from_field.base_type,
                            schema_ref: None,
                            constraints: from_field.constraints.clone(),
                            optional: from_field.optional,
                        },
                        location: contract.from_schema.location.clone(),
                        message: format!(
                            "Field '{}' may require normalization (pattern validation expected)",
                            field_name
                        ),
                    });
                }
            }
        }

        mismatches
    }

    fn name(&self) -> &str {
        "unnormalized_data"
    }
}
