# Change Log
All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](https://semver.org).

## [Unreleased]
### Added
- New Operators
  - `add` (`+`)
  - `sub` (`-`)
  - `mul` (`*`)
  - `div` (`/`)
- Meta-functions (prefixed with `#`)
- Tree-based type hierarchy
- Python-function to Tea-function bindings
- Context-based library import
- Variable declarations, assignments
- Tests for `runtime.lexer`

### Changed
- Light bindings between the runtime environment and the runtime library
- Seperated the runtime environment from the runtime library
- Renamed `runtime.tokenizer` to `runtime.lexer`

## [v0.0.3]
### Added
- String literals
- Abstract syntax tree evaluation
- Startup scripts
- Test cases for runtime.ast and runtime.std
- Basic type system
- Support for functions and operators

### Changed
- Enhanced tokenizer speed
- Splitted up runtime and REPL interface
- Seperated the executor into the abstract syntax tree and the standard runtime environment

## [v0.0.2]
### Added
- Basic command line inteface for REPL-mode
- Simple tokenizer supporting operators, whitespace, identifiers and numbers

### Fixed
- Wrong CLI version number


[Unreleased]: https://github.com/lnsp/tea/compare/v0.0.3...master
[v0.0.3]: https://github.com/lnsp/tea/compare/v0.0.2...v0.0.3
[v0.0.2]: https://github.com/lnsp/tea/compare/v0.0.1...v0.0.2
