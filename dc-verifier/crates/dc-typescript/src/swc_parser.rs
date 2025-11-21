use anyhow::Result;
use std::path::Path;
use swc_common::{FileName, SourceMap};
use swc_ecma_ast::*;
use swc_ecma_parser::{Parser, StringInput, Syntax, TsConfig};

/// Парсер TypeScript через swc
pub struct SwcParser {
    source_map: SourceMap,
}

impl SwcParser {
    /// Создает новый парсер
    pub fn new() -> Self {
        Self {
            source_map: SourceMap::default(),
        }
    }

    /// Парсит файл TypeScript/JavaScript
    pub fn parse_file(&self, path: &Path) -> Result<Module> {
        let source = std::fs::read_to_string(path)?;
        self.parse_source(&source, path)
    }

    /// Парсит исходный код
    pub fn parse_source(&self, source: &str, path: &Path) -> Result<Module> {
        let fm = self
            .source_map
            .new_source_file(FileName::Real(path.to_path_buf()), source.to_string());

        let syntax = Syntax::Typescript(TsConfig {
            tsx: path.extension().and_then(|e| e.to_str()) == Some("tsx"),
            decorators: true,
            ..Default::default()
        });

        let mut parser = Parser::new_from(syntax, StringInput::from(&*fm), None);

        parser
            .parse_module()
            .map_err(|e| anyhow::anyhow!("Parse error: {:?}", e))
    }
}

impl Default for SwcParser {
    fn default() -> Self {
        Self::new()
    }
}
