# parser.py
try:
    from scanner2 import tokenize, Token
except ImportError:
    print("Error: Could not find 'scanner2.py'. Make sure it's in the same directory as this parser file.")
    exit()

class ASTNode:
    def __repr__(self):
        fields = {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
        field_str = ", ".join(f"{k}={v!r}" for k, v in fields.items())
        return f"{self.__class__.__name__}({field_str})"

class Program(ASTNode):
    def __init__(self, statements):
        self.statements = statements

class FuncDef(ASTNode):
    def __init__(self, func_name, params, body):
        self.func_name = func_name
        self.params = params    # list of VarDecl (with var_type, var_name)
        self.body = body        # list of statements

class VarDecl(ASTNode):
    def __init__(self, var_type, var_name, initializer):
        self.var_type = var_type
        self.var_name = var_name
        self.initializer = initializer

class IfStmt(ASTNode):
    def __init__(self, condition, if_block, else_block):
        self.condition = condition
        self.if_block = if_block
        self.else_block = else_block

class OutputStmt(ASTNode):
    def __init__(self, expression):
        self.expression = expression

class InputStmt(ASTNode):
    def __init__(self, identifier):
        self.identifier = identifier

class ForLoop(ASTNode):
    def __init__(self, initializer, condition, increment, body):
        self.initializer = initializer
        self.condition = condition
        self.increment = increment
        self.body = body

class WhileLoop(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class DoWhileLoop(ASTNode):
    def __init__(self, body, condition):
        self.body = body
        self.condition = condition

class ReturnStmt(ASTNode):
    def __init__(self, expression):
        self.expression = expression

class PauseStmt(ASTNode): pass
class Empty(ASTNode): pass

class Assignment(ASTNode):
    def __init__(self, identifier, expression):
        self.identifier = identifier  # Identifier
        self.expression = expression

class FuncCall(ASTNode):
    def __init__(self, identifier, args):
        self.identifier = identifier  # Identifier
        self.args = args

class BinaryOp(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op  # token object
        self.right = right

class Literal(ASTNode):
    def __init__(self, value, type):
        self.value = value
        self.type = type  # token type string (e.g., NUMBER_INT, STRING, BOOL_LITERAL)

class Identifier(ASTNode):
    def __init__(self, name):
        self.name = name


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current_token(self):
        return self.tokens[self.pos]

    def advance(self):
        token = self.current_token()
        self.pos += 1
        return token

    def consume(self, expected_type, error_message):
        token = self.current_token()
        if token.type == expected_type:
            return self.advance()
        raise SyntaxError(f"{error_message}. Expected {expected_type} but got {token.type} (Line {token.line})")

    def match(self, *types_to_match):
        token = self.current_token()
        if token.type in types_to_match:
            self.advance()
            return True
        return False

    def parse(self):
        statements = []
        while self.current_token().type != 'EOF':
            statements.append(self.parse_statement())
        return Program(statements)

    def parse_statement(self):
        token_type = self.current_token().type

        if token_type == 'FUNC_DEF':
            return self.parse_function_definition()
        elif token_type == 'MAIN_FUNC':
            return self.parse_main_block()
        elif token_type in ('TYPE_INT', 'TYPE_FLOAT', 'TYPE_STRING', 'TYPE_BOOL'):
            return self.parse_variable_declaration()
        elif token_type == 'IF_STMT':
            return self.parse_if_statement()
        elif token_type == 'OUTPUT_STMT':
            return self.parse_output_statement()
        elif token_type == 'INPUT_STMT':
            return self.parse_input_statement()
        elif token_type == 'FOR_LOOP':
            return self.parse_for_loop()
        elif token_type == 'WHILE_LOOP':
            return self.parse_while_loop()
        elif token_type == 'DO_WHILE_START':
            return self.parse_do_while_loop()
        elif token_type == 'RETURN_STMT':
            return self.parse_return_statement()
        elif token_type == 'PAUSE_STMT':
            return self.parse_pause_statement()
        elif token_type == 'ID':
            next_token_type = self.tokens[self.pos + 1].type
            if next_token_type == 'OP_ASSIGN':
                return self.parse_assignment_statement()
            elif next_token_type == 'LBRAC':
                call = self.parse_primary()
                self.consume('SCOLON', "Expected ';' after function call statement.")
                return call
            else:
                raise SyntaxError(f"Unexpected ID '{self.current_token().value}'. Expected '=' or '('. (Line {self.current_token().line})")
        else:
            raise SyntaxError(f"Unexpected token {self.current_token().value} (Line {self.current_token().line})")

    def parse_function_definition(self):
        self.consume('FUNC_DEF', "Expected 'dream'")
        name = self.consume('ID', "Expected function name").value
        self.consume('LBRAC', "Expected '(' after function name")
        params = []
        if self.current_token().type != 'RBRAC':
            params = self.parse_parameter_list()
        self.consume('RBRAC', "Expected ')' after parameters")
        body = self.parse_block()
        return FuncDef(name, params, body)

    def parse_parameter_list(self):
        params = []
        param_type = self.advance()  # Consumes TYPE token
        param_name = self.consume('ID', "Expected parameter name").value
        params.append(VarDecl(param_type.type, param_name, None))
        while self.match('COMMA'):
            param_type = self.advance()  # Consumes TYPE
            param_name = self.consume('ID', "Expected parameter name").value
            params.append(VarDecl(param_type.type, param_name, None))
        return params

    def parse_main_block(self):
        self.consume('MAIN_FUNC', "Expected 'rest'")
        body = self.parse_block()
        return FuncDef('__main__', [], body)

    def parse_block(self):
        self.consume('CLBRAC', "Expected '{' to start a block")
        statements = []
        while self.current_token().type not in ('CRBRAC', 'EOF'):
            statements.append(self.parse_statement())
        self.consume('CRBRAC', "Expected '}' to end a block")
        return statements

    def parse_variable_declaration(self, consume_semicolon=True):
        var_type = self.advance()  # Consumes TYPE token (e.g., TYPE_INT)
        var_name = self.consume('ID', "Expected variable name").value
        initializer = None
        if self.match('OP_ASSIGN'):
            initializer = self.parse_expression()
        if consume_semicolon:
            self.consume('SCOLON', "Expected ';' after variable declaration")
        return VarDecl(var_type.type, var_name, initializer)

    def parse_if_statement(self):
        self.consume('IF_STMT', "Expected 'ifawake'")
        self.consume('LBRAC', "Expected '(' after 'ifawake'")
        condition = self.parse_expression()
        self.consume('RBRAC', "Expected ')' after if condition")
        if_block = self.parse_block()
        else_block = None
        if self.match('ELSE_STMT'):
            else_block = self.parse_block()
        return IfStmt(condition, if_block, else_block)

    def parse_output_statement(self):
        self.consume('OUTPUT_STMT', "Expected 'bed'")
        self.consume('LBRAC', "Expected '(' after 'bed'")
        expression = self.parse_expression()
        self.consume('RBRAC', "Expected ')' after output expression")
        self.consume('SCOLON', "Expected ';' after 'bed' statement")
        return OutputStmt(expression)

    def parse_input_statement(self):
        self.consume('INPUT_STMT', "Expected 'pillow'")
        self.consume('LBRAC', "Expected '(' after 'pillow'")
        ident = Identifier(self.consume('ID', "Expected variable name to store input").value)
        self.consume('RBRAC', "Expected ')' after variable name")
        self.consume('SCOLON', "Expected ';' after 'pillow' statement")
        return InputStmt(ident)

    def parse_for_loop(self):
        self.consume('FOR_LOOP', "Expected 'countsheep'")
        self.consume('LBRAC', "Expected '(' after 'countsheep'")
        initializer = None
        if self.current_token().type in ('TYPE_INT', 'TYPE_FLOAT', 'TYPE_STRING', 'TYPE_BOOL'):
            initializer = self.parse_variable_declaration(consume_semicolon=False)
        elif self.current_token().type != 'SCOLON':
            initializer = self.parse_expression()
        self.consume('SCOLON', "Expected ';' after for-loop initializer")
        condition = None
        if self.current_token().type != 'SCOLON':
            condition = self.parse_expression()
        self.consume('SCOLON', "Expected ';' after for-loop condition")
        increment = None
        if self.current_token().type != 'RBRAC':
            increment = self.parse_expression()
        self.consume('RBRAC', "Expected ')' to end for-loop header")
        body = self.parse_block()
        return ForLoop(initializer, condition, increment, body)

    def parse_while_loop(self):
        self.consume('WHILE_LOOP', "Expected 'whiledreaming'")
        self.consume('LBRAC', "Expected '(' after 'whiledreaming'")
        condition = self.parse_expression()
        self.consume('RBRAC', "Expected ')' after while condition")
        body = self.parse_block()
        return WhileLoop(condition, body)

    def parse_do_while_loop(self):
        self.consume('DO_WHILE_START', "Expected 'snooze'")
        body = self.parse_block()
        self.consume('WHILE_LOOP', "Expected 'whiledreaming' after 'snooze' block")
        self.consume('LBRAC', "Expected '(' after 'whiledreaming'")
        condition = self.parse_expression()
        self.consume('RBRAC', "Expected ')' after do-while condition")
        self.consume('SCOLON', "Expected ';' after do-while statement")
        return DoWhileLoop(body, condition)

    def parse_return_statement(self):
        self.consume('RETURN_STMT', "Expected 'awaken'")
        expression = None
        if self.current_token().type != 'SCOLON':
            expression = self.parse_expression()
        self.consume('SCOLON', "Expected ';' after return statement")
        return ReturnStmt(expression)

    def parse_pause_statement(self):
        self.consume('PAUSE_STMT', "Expected 'snore'")
        self.consume('SCOLON', "Expected ';' after 'snore'")
        return PauseStmt()

    def parse_assignment_statement(self):
        ident = Identifier(self.consume('ID', "Expected identifier").value)
        self.consume('OP_ASSIGN', "Expected '=' for assignment")
        expression = self.parse_expression()
        self.consume('SCOLON', "Expected ';' after assignment")
        return Assignment(ident, expression)

    # Expression parsing (precedence aware)
    def parse_expression(self):
        return self.parse_equality()

    def parse_equality(self):
        left = self.parse_comparison()
        while (self.current_token().type == 'OP_REL' and self.current_token().value in ('==', '!=')):
            op = self.advance()
            right = self.parse_comparison()
            left = BinaryOp(left, op, right)
        return left

    def parse_comparison(self):
        left = self.parse_term()
        while (self.current_token().type == 'OP_REL' and self.current_token().value in ('<', '>', '<=', '>=')):
            op = self.advance()
            right = self.parse_term()
            left = BinaryOp(left, op, right)
        return left

    def parse_term(self):
        left = self.parse_factor()
        while (self.current_token().type == 'OP_ARITH' and self.current_token().value in ('+', '-')):
            op = self.advance()
            right = self.parse_factor()
            left = BinaryOp(left, op, right)
        return left

    def parse_factor(self):
        left = self.parse_primary()
        while (self.current_token().type == 'OP_ARITH' and self.current_token().value in ('*', '/', '%')):
            op = self.advance()
            right = self.parse_primary()
            left = BinaryOp(left, op, right)
        return left

    def parse_primary(self):
        if self.match('NUMBER_INT', 'NUMBER_FLOAT', 'STRING', 'BOOL_LITERAL'):
            token = self.tokens[self.pos - 1]
            return Literal(token.value, token.type)

        if self.current_token().type == 'ID':
            if self.tokens[self.pos + 1].type == 'LBRAC':
                return self.parse_function_call()
            else:
                return Identifier(self.advance().value)

        if self.match('LBRAC'):
            expr = self.parse_expression()
            self.consume('RBRAC', "Expected ')' after grouped expression")
            return expr
        
        raise SyntaxError(f"Unexpected token in expression: {self.current_token().value} (Line {self.current_token().line})")

    def parse_function_call(self):
        ident = Identifier(self.advance().value)
        self.consume('LBRAC', "Expected '(' for function call")
        args = []
        if self.current_token().type != 'RBRAC':
            args = self.parse_argument_list()
        self.consume('RBRAC', "Expected ')' to end function call")
        return FuncCall(ident, args)

    def parse_argument_list(self):
        args = []
        args.append(self.parse_expression())
        while self.match('COMMA'):
            args.append(self.parse_expression())
        return args
