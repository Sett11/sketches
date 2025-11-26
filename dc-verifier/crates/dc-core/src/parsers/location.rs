/// Конвертер байтовых смещений в номера строк и колонок
/// Используется для точного преобразования TextSize из rustpython-parser в Location
pub struct LocationConverter {
    source: String,
    line_starts: Vec<usize>,
}

impl LocationConverter {
    /// Создает новый LocationConverter из исходного кода
    pub fn new(source: String) -> Self {
        let line_starts = Self::calculate_line_starts(&source);
        Self { source, line_starts }
    }

    /// Конвертирует байтовое смещение в номер строки и колонки (1-based)
    pub fn byte_offset_to_location(&self, offset: usize) -> (usize, usize) {
        if offset > self.source.len() {
            // Если смещение выходит за границы, возвращаем последнюю строку
            let last_line = self.line_starts.len().max(1);
            let last_col = self.source.len().saturating_sub(
                *self.line_starts.last().unwrap_or(&0)
            ).max(1);
            return (last_line, last_col);
        }

        // Бинарный поиск строки, содержащей offset
        let (line, line_start_pos) = match self.line_starts.binary_search(&offset) {
            Ok(idx) => {
                // Точное совпадение - начало строки idx+1 (1-based)
                (idx + 1, self.line_starts[idx])
            }
            Err(idx) => {
                // idx указывает на позицию вставки
                // offset находится в строке idx (1-based)
                let line_num = idx.max(1);
                let line_start = if idx == 0 {
                    0
                } else {
                    self.line_starts[idx - 1]
                };
                (line_num, line_start)
            }
        };

        let column = offset.saturating_sub(line_start_pos) + 1;
        (line, column)
    }

    /// Вычисляет позиции начала каждой строки (в байтах)
    fn calculate_line_starts(source: &str) -> Vec<usize> {
        let mut line_starts = vec![0]; // Первая строка начинается с 0
        let mut current_pos = 0;

        for byte in source.bytes() {
            current_pos += 1;
            if byte == b'\n' {
                line_starts.push(current_pos);
            }
        }

        line_starts
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_simple_conversion() {
        let source = "line1\nline2\nline3".to_string();
        let converter = LocationConverter::new(source);

        // Начало первой строки
        assert_eq!(converter.byte_offset_to_location(0), (1, 1));
        
        // Конец первой строки (перед \n)
        assert_eq!(converter.byte_offset_to_location(5), (1, 6));
        
        // Начало второй строки (после \n)
        assert_eq!(converter.byte_offset_to_location(6), (2, 1));
        
        // Середина второй строки
        assert_eq!(converter.byte_offset_to_location(8), (2, 3));
    }

    #[test]
    fn test_empty_source() {
        let source = String::new();
        let converter = LocationConverter::new(source);
        assert_eq!(converter.byte_offset_to_location(0), (1, 1));
    }

    #[test]
    fn test_offset_out_of_bounds() {
        let source = "line1\nline2".to_string();
        let converter = LocationConverter::new(source);
        
        // offset за пределами
        let (line, col) = converter.byte_offset_to_location(1000);
        assert!(line >= 1);
        assert!(col >= 1);
    }
}

