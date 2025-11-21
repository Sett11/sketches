use anyhow::Result;
use std::path::{Path, PathBuf};

/// Находит точку входа в приложение
pub fn find_entry_point(project_root: &Path, custom_entry: Option<&str>) -> Result<PathBuf> {
    // Если указана кастомная точка входа
    if let Some(entry) = custom_entry {
        let path = project_root.join(entry);
        if path.exists() {
            return Ok(path);
        }
        anyhow::bail!("Custom entry point not found: {}", entry);
    }

    // Ищем стандартные точки входа
    let candidates = ["main.py", "app.py", "__main__.py", "server.py"];

    for candidate in &candidates {
        let path = project_root.join(candidate);
        if path.exists() {
            return Ok(path);
        }
    }

    anyhow::bail!(
        "Entry point not found in {:?}. Tried: {:?}",
        project_root,
        candidates
    )
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;
    use tempfile::TempDir;

    #[test]
    fn test_find_entry_point() {
        let temp_dir = TempDir::new().unwrap();
        let project_root = temp_dir.path();

        // Создаем app.py
        fs::write(project_root.join("app.py"), "from fastapi import FastAPI\n").unwrap();

        let entry = find_entry_point(project_root, None).unwrap();
        assert!(entry.ends_with("app.py"));
    }
}
