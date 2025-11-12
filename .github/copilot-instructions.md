# AI Coding Agent Instructions - dialogos_a_español

## Project Overview

Spanish narrative dialog converter that transforms quoted dialogue (`"text"`) to editorial Spanish format with em dashes (`—text`). Supports both TXT and ODT (LibreOffice) files with comprehensive RAE-compliant rules.

## Architecture Components

### Core Conversion Engine (`src/converter.py`)

- **DialogConverter**: Main conversion logic with 5 distinct rules (D1-D5)
- **Pattern matching**: Handles ASCII quotes (`"` `'`) and typographic quotes (`"` `"` `'` `'`)
- **Rule priority**: D2 (dialog tags) → D1 (standalone) → D5 (nested quotes)
- **Line-by-line processing** with context awareness for speaker continuation

### ODT Document Handling (`src/odt_handler.py`)

- **ODTProcessor**: Preserves complete document structure (styles, formatting, metadata)
- **Known limitation**: Inline formatting (bold/italic) lost in paragraphs with line-breaks
- **Structure preservation**: Uses XML manipulation to maintain document integrity
- **Namespace handling**: Registers all ODT XML namespaces to prevent corruption

### Conversion Rules (`src/rules.py`)

- **42 dialog tags** (verbos dicendi): `dijo`, `preguntó`, `respondió`, `murmuró`, etc.
- **Spanish-specific patterns**: Recognizes interrogation/exclamation marks, comma handling
- **Context detection**: Distinguishes internal quotes vs. speaker continuation

## Essential Development Workflows

### Testing Strategy

```bash
# Run all tests (26 tests, must be 100% passing)
python -m unittest discover tests -v

# Quick project verification
./verify.sh

# Test specific converter behavior
python -m unittest tests.test_converter -v
```

### CLI Usage Patterns

```bash
# Basic conversion (auto-detects .odt vs .txt)
python -m src.main input.txt
python -m src.main document.odt

# Always generates TWO files:
# 1. {name}_convertido.txt/.odt (converted text)
# 2. {name}_convertido.log.txt (detailed change log)
```

### Programmatic Usage

```python
from src.converter import DialogConverter
from src.odt_handler import ODTProcessor

# Text conversion
converter = DialogConverter()
converted_text, logger = converter.convert(original_text)

# ODT processing (preserves structure)
processor = ODTProcessor(Path('input.odt'))
processor.process_and_save(Path('output.odt'), converter.convert)
```

## Critical Project Patterns

### Error Handling Philosophy

- **File validation first**: Check existence, type, ODT structure before processing
- **Graceful degradation**: ODT issues fall back to text-only processing
- **Detailed logging**: Every change logged with line numbers, original/converted text, rule applied

### Code Organization Principles

- **Separation of concerns**: converter logic separate from file I/O, logging, CLI
- **Stateful conversion**: DialogConverter tracks line numbers for accurate logging
- **Immutable transformations**: Original files never modified, always create new files

### Spanish Editorial Rules Implementation

```python
# D1: Quote substitution - "text" → —text
# D2: Dialog tags - "text" dijo → —text —dijo
# D3: Punctuation handling - "text?" → —text?
# D4: Speaker continuation - "text" dijo. "more" → —text —dijo. —more
# D5: Nested quotes - 'internal' → «internal»
```

### Version Management

- Version defined in `src/__init__.py` and CLI help
- Changelog driven development in `CHANGELOG.md`
- Known limitations documented (ODT inline formatting)

## Common Debugging Patterns

### ODT Processing Issues

- Check `content.xml` extraction in `ODTReader.extract_text()`
- Line-break handling in `ODTProcessor._convert_with_line_breaks()`
- Namespace preservation issues → verify `ET.register_namespace()` calls

### Conversion Logic Issues

- **Rule precedence**: D2 patterns should process before D1 to avoid conflicts
- **Spanish context**: Check verb recognition in `is_dialog_tag()`
- **Quote type handling**: Both ASCII and Unicode quote variants must be supported

### Testing New Rules

- Add test cases to `tests/test_converter.py`
- Use `examples/` directory for manual testing
- Verify both TXT and ODT output formats
- Check conversion logger captures all changes

## File Dependencies

- **Zero external dependencies**: Only Python standard library
- **Python 3.11+ required** for modern syntax
- **ODT = ZIP + XML**: Standard OpenDocument format, no external libraries
- **Encoding**: Always UTF-8 for proper Spanish character support

When modifying conversion logic, always test with `examples/ejemplo_largo.txt` (complex scenarios) and verify the generated `.log.txt` accurately captures all transformations.
