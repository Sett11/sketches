# Contributing to DCV

Thank you for your interest in contributing to DCV (Data Chains Verifier)!

## Development Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Ensure all tests pass (`cargo test --all`)
5. Ensure code compiles without warnings (`cargo check --all`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## Code Standards

### Language
- **Comments**: All code comments and documentation should be in English
- **Variable names**: Use English names
- **Function names**: Use English names

### Code Formatting
- Use `cargo fmt` to format code before committing
- Use `cargo clippy` to check for common issues

### Documentation
- All public functions and structs must have doc comments (`///`)
- Include examples in doc comments where appropriate
- Use standard Rust doc comment format

## Running Tests

```bash
# Run all tests
cargo test --all

# Run tests for a specific crate
cargo test -p dc-core

# Run tests with output
cargo test --all -- --nocapture
```

## Adding a New Adapter

To add support for a new language/framework:

1. Create a new crate in `crates/dc-<adapter-name>/`
2. Implement the parser in `src/parsers/` (if needed)
3. Implement the call graph builder in `src/call_graph.rs`
4. Add the adapter to `dc-cli/src/commands/check.rs`
5. Add tests in `tests/`
6. Update documentation

## Code Review Process

1. All PRs require at least one approval
2. Code must pass all CI checks
3. Maintainers will review for:
   - Code quality
   - Test coverage
   - Documentation completeness
   - Performance considerations

## Questions?

If you have questions, please open an issue or contact the maintainers.

