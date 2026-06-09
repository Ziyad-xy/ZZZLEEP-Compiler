# main.py
from scanner2 import tokenize , Token
from parser import Parser
from symboltable import SemanticAnalyzer
import pprint
import sys
import os

if __name__ == "__main__":
    file_path = r"F:\project python\complier2\examplescanner2.txt"

    if not os.path.isfile(file_path):
        print(f"Error: source file not found: {file_path}")
        sys.exit(1)

    tokens = tokenize(file_path)
    if not tokens:
        print("Tokenization failed (no tokens produced).")
        sys.exit(1)

    # parse
    parser = Parser(tokens)
    try:
        ast = parser.parse()
    except SyntaxError as e:
        print("\n[SYNTAX ERROR]")
        print(e)
        sys.exit(1)
    except Exception as e:
        print("\n[UNEXPECTED PARSER ERROR]")
        print(e)
        sys.exit(1)

    # semantic analysis
    analyzer = SemanticAnalyzer()


    errors = analyzer.analyze(ast)

    print("\n===== AST =====")
    pprint.pprint(ast)

    print("\n===== Semantic Errors =====")
    if analyzer.errors:
        for err in analyzer.errors:
            print(" •", err)
    else:
        print("No errors ✓")

    print("\n===== Function Table =====")

    readable = {}
    for fname, info in analyzer.functions.items():
        readable[fname] = {'params': info['params'], 'return': info['return']}
    pprint.pprint(readable)
