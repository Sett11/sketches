use anyhow::Result;
use std::path::Path;
use swc_common::{sync::Lrc, FileName, SourceMap};
use swc_ecma_ast::*;
use swc_ecma_parser::{lexer::Lexer, Parser, StringInput, Syntax};

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
        let file_name: Lrc<FileName> = FileName::Real(path.to_path_buf()).into();
        let fm = self
            .source_map
            .new_source_file(file_name, source.to_string());

        let is_tsx = path.extension().and_then(|e| e.to_str()) == Some("tsx");
        let syntax = if is_tsx {
            Syntax::Typescript(Default::default())
        } else {
            Syntax::Typescript(Default::default())
        };

        let lexer = Lexer::new(syntax, Default::default(), StringInput::from(&*fm), None);
        let mut parser = Parser::new_from(lexer);

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
