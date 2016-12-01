# Change Log
All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](https://semver.org).

## [Unreleased]
### Added
- Working token-to-AST parser
- Run `tea [file]` to execute a Tea script>
- New `while` statement for basic loops
- New `for` statement for iteration loops
- New `func` statement for defining functions
- New `if-else` statement for branching
- Support for comparison operators in lexer
- Support for type interference on declaration
- Support for multi-variable declarations
- Support for multi-bound operators like `+`
- Support for escape codes in string sequences
- New operators
  - `and` (`&&`)
  - `or` (`||`)
  - `xor` (`^|`)
  - `equ` (`==`)
  - `neq` (`!=`)
  - `sm` (`<`)
  - `lg` (`>`)
  - `sme` (`<=`)
  - `lge` (`>=`)
  - `unmi` (`-`)
  - `unpl` (`+`)
  - `uninv` (`!`)
  - `mod` (`%`)
  - `pow` (`^`)
- New persistent runtime flag storage
- Advanced type formatting
- Fibonacci demo script in compatible Tea
- repl.py has now its own support library

### Changed
- Reduce print-statement console clustering, debug mode can be enabled via `\debug` CLI command
- Enable auto-casting on assignment
- Improve identifier parsing
- Replace ADD and SUB operators with PLUS and minus to reflect their new roles
- CLI now only catches exceptions that were raised by the Tea runtime
- Use `\\` instead of `#` as escape symbol in REPL CLI

### Fixed
- Operator exception handling now handles multi-signatures bounds correctly
- Null-to-boolean casting works correctly now
- Equality operator parsing now generates one token instead of two

## [v0.0.4]
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
- New, shiny logo
- Travis CI integration for build status and tests

### Changed
- Light bindings between the runtime environment and the runtime library
- Seperated the runtime environment from the runtime library
- Renamed `runtime.tokenizer` to `runtime.lexer`
- Rename all `...Error` to `...Exception` for better distinction
- Massive code quality improvements, enhancements to style and structure

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


[Unreleased]: https://github.com/lnsp/tea/compare/v0.0.4...master
[v0.0.4]: https://github.com/lnsp/tea/compare/v0.0.3...v0.0.4
[v0.0.3]: https://github.com/lnsp/tea/compare/v0.0.2...v0.0.3
[v0.0.2]: https://github.com/lnsp/tea/compare/v0.0.1...v0.0.2
