# ZZZleep Language Compiler

This repository contains a small compiler front-end for a toy language nicknamed "Sleep Language". The project performs lexical analysis (tokenization), parsing into an AST, basic semantic analysis (type checking, symbol/function tables), and includes simple visualization and a Streamlit GUI wrapper.

## Quick Overview

- Lexer: `scanner2.py` — reads a source file and converts it into a linear stream of tokens.
- Parser: `parser.py` — consumes tokens and builds an AST (Program, FuncDef, VarDecl, IfStmt, etc.).
- Semantic Analyzer: `symboltable.py` — two-pass analysis that collects function signatures then type-checks function bodies and the implicit `__main__` block, recording semantic errors and a function table.
- Visualizer: `run.py` — simple AST visualizer that pretty-prints the AST tree.
- CLI Entrypoint: `main.py` — runs the full pipeline (tokenize → parse → semantic analysis) and prints AST, semantic errors, and the function table.
- GUI: `gui.py` — Streamlit front-end that writes the editor contents to `examplescanner2.txt` and runs `main.py` as a subprocess to show results.

## File Map

- `examplescanner2.txt` — default sample source file used by the scripts and GUI.
- `examples.txt` — additional example inputs (may be unused by other scripts).
- `scanner2.py` — tokenizer implementation (regex-based). Produces `Token(type, value, line)` namedtuples and appends an `EOF` token.
- `parser.py` — recursive-descent parser. Produces AST node classes such as `Program`, `FuncDef`, `VarDecl`, `IfStmt`, `ForLoop`, `WhileLoop`, `BinaryOp`, `Literal`, `Identifier`, and `FuncCall`.
- `symboltable.py` — semantic analyzer with scoping, variable declarations, function signatures, return type inference, and type unification rules.
- `run.py` — helper to lex, parse, and visualize AST on the console.
- `main.py` — full pipeline runner used by `gui.py` and for command-line compilation.
- `gui.py` — Streamlit UI to edit source and invoke `main.py`.

## Logic Flow (End-to-end)

1. Source input: a Sleep Language source file (`examplescanner2.txt` by default) is read.
2. Tokenization (`scanner2.tokenize`): the lexer uses regex patterns and a keyword map to convert text into a list of `Token(type, value, line)` objects. Unrecognized characters are reported, and a final `EOF` token is appended.
3. Parsing (`Parser` in `parser.py`): a recursive-descent parser advances through tokens and constructs an AST composed of the node classes defined in `parser.py`. The parser recognizes function definitions (`dream`), the `rest` main block, variable declarations, control flow (ifawake, countsheep, whiledreaming, snooze), I/O (`bed`, `pillow`), returns (`awaken`), and expressions with operator precedence.
4. Semantic analysis (`SemanticAnalyzer` in `symboltable.py`):
   - First pass: collect function signatures (names and parameter types) into a function table.
   - Second pass: analyze each function body (and the implicit `__main__` top-level block) with scoped symbol tables.
   - Type checks: variable initializers, assignments, arithmetic, comparisons, function calls (argument counts and types), and return types. The analyzer records errors in `self.errors` and builds a human-readable function table.
5. Output (`main.py` / `gui.py`): the pipeline prints the AST, lists semantic errors (if any), and shows a function table (parameter & return types). The Streamlit GUI writes the editor text to `examplescanner2.txt` and runs `main.py` as a subprocess to capture and present results.

## How to Run

Prerequisite: Python 3.8+ (modules used are in the standard library). For the GUI you need `streamlit` installed.

Command-line examples:

Run full compile pipeline (lex → parse → semantic):

```bash
python main.py
```

Visualize AST with the tree printer:

```bash
python run.py
```

Run the Streamlit GUI (web UI):

```bash
pip install streamlit
streamlit run gui.py
```

Notes:
- `main.py` defaults to reading `examplescanner2.txt` from the project root — either edit that file or run the GUI to supply new code.
- The lexer recognizes Sleep Language keywords like `dream`, `rest`, `bed`, `pillow`, `ifawake`, `countsheep`, `whiledreaming`, `snooze`, `snore`, etc.

## Examples

Use `examplescanner2.txt` as a starting point. The parser and analyzer will report syntax and semantic errors with line numbers when possible.

## Next Steps / Improvements

- Add an AST-to-bytecode or AST-to-source transpiler to generate output code.
- Improve error messages to include token context and source excerpts.
- Add unit tests for lexer, parser, and semantic analyzer.
