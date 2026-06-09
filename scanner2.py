# scanner2.py
import re
from collections import namedtuple

Token = namedtuple('Token', ['type', 'value', 'line'])

def tokenize(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
    except FileNotFoundError:
        print(f"Error: Could not find file '{file_path}'")
        return []
    except Exception as e:
        print(f"Error opening file: {e}")
        return []
    
    tokenSpecification = [
        ('COMMENT',     r'zzz.*'),
        ('STRING',      r'"(\\.|[^"\\])*"'),
        ('TYPE_INT',    r'\b(hush)\b'),
        ('TYPE_FLOAT',  r'\b(silence)\b'),
        ('TYPE_STRING', r'\b(whisper)\b'),
        ('TYPE_BOOL',   r'\b(lucid)\b'),
        ('KEYWORD',     r'\b(dream|rest|awaken|bed|pillow|ifawake|elsesleep|countsheep|whiledreaming|snooze|snore|ZZZ|sleepscape)\b'),
        ('NUMBER_FLOAT',r'\d+\.\d+'),
        ('NUMBER_INT',  r'\d+'),
        ('BOOL_LITERAL',r'\b(true|false)\b'),
        ('ID',          r'[a-zA-Z_][a-zA-Z0-9_]*'),
        ('OP_REL',      r'(==|!=|<=|>=|<|>)'), 
        ('OP_ASSIGN',   r'='),
        ('OP_ARITH',    r'[+\-*/%]'),
        ('LBRAC',       r'\('),
        ('RBRAC',       r'\)'),
        ('CLBRAC',      r'\{'),
        ('CRBRAC',      r'\}'),
        ('LSQBRAC',     r'\['),
        ('RSQBRAC',     r'\]'),
        ('SCOLON',      r';'),
        ('COMMA',       r','),
        ('DOT',         r'\.'),
        ('NEWLINE',     r'\n'),
        ('SKIP',        r'[ \t]+'),
        ('UNKNOWN',     r'.')
    ]

    keyword_map = {
        "dream": "FUNC_DEF",
        "rest": "MAIN_FUNC",
        "awaken": "RETURN_STMT",
        "bed": "OUTPUT_STMT",
        "pillow": "INPUT_STMT",
        "ifawake": "IF_STMT",
        "elsesleep": "ELSE_STMT",
        "countsheep": "FOR_LOOP",
        "whiledreaming": "WHILE_LOOP",
        "snooze": "DO_WHILE_START",
        "snore": "PAUSE_STMT",
        "ZZZ": "INCLUDE_LIB",
        "sleepscape": "NAMESPACE_DEF",
    }
    
    regex = '|'.join(f'(?P<{pair[0]}>{pair[1]})' for pair in tokenSpecification)
    
    line = 1
    tokens = [] 
    
    for matching in re.finditer(regex, code):
        kind = matching.lastgroup
        value = matching.group()

        if kind == 'NEWLINE':
            line += 1
            continue
        elif kind == 'SKIP' or kind == 'COMMENT':
            continue
        elif kind == 'UNKNOWN':
            print(f"[Line {line:<2}] | ERROR | Unrecognized token: '{value}'")
            continue
        else:
            if kind == 'KEYWORD':
                kind = keyword_map.get(value, kind)
            
            tokens.append(Token(kind, value, line))
            
    tokens.append(Token('EOF', None, line))
    return tokens
