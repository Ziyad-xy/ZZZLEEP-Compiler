from parser import FuncDef, VarDecl, Assignment, FuncCall, BinaryOp, Literal, Identifier, IfStmt, ReturnStmt, OutputStmt, ForLoop, WhileLoop, DoWhileLoop, InputStmt
from collections import deque

class SemanticAnalyzer:
    def __init__(self):
        
        self.functions = {}
        self.scopes = []
        self.current_function = None
        self.errors = []

    def error(self, msg):
        self.errors.append(msg)

    def push_scope(self):
        self.scopes.append({})

    def pop_scope(self):
        if self.scopes:
            self.scopes.pop()

    def declare_var(self, name, vtype):
        if not self.scopes:
            self.push_scope()
        if name in self.scopes[-1]:
            self.error(f"Variable '{name}' already declared in this scope (function '{self.current_function}').")
        else:
            self.scopes[-1][name] = vtype

    def lookup_var(self, name):
        for s in reversed(self.scopes):
            if name in s:
                return s[name]
        self.error(f"Use of undeclared variable '{name}' in function '{self.current_function}'.")
        return None

    
    def declare_function(self, name, param_types, node):
        if name in self.functions:
            self.error(f"Function '{name}' already defined.")
        else:
            self.functions[name] = {'params': param_types, 'return': None, 'node': node}

    def set_function_return(self, name, rtype):
        entry = self.functions.get(name)
        if entry is None:
            return
        if entry['return'] is None:
            entry['return'] = rtype
        else:
            if entry['return'] != rtype and rtype is not None:
                # allow NUMBER_INT -> TYPE_FLOAT promotion? For simplicity we do not auto-promote here.
                self.error(f"Inconsistent return types in function '{name}': {entry['return']} vs {rtype}")

    
    def literal_to_type(self, literal_token_type):
        if literal_token_type == 'NUMBER_INT':
            return 'TYPE_INT'
        if literal_token_type == 'NUMBER_FLOAT':
            return 'TYPE_FLOAT'
        if literal_token_type == 'STRING':
            return 'TYPE_STRING'
        if literal_token_type == 'BOOL_LITERAL':
            return 'TYPE_BOOL'
        return None


    
    def unify(self, t1, t2, context=""):
        if t1 is None or t2 is None:
            return None

        if t1 == t2:
            return t1

        if 'TYPE_BOOL' in (t1, t2):
            self.error(
                f"Type mismatch{(' in ' + context) if context else ''}: {t1} vs {t2} "
                f"(function '{self.current_function}')."
            )
            return None


        if (t1 == 'TYPE_INT' and t2 == 'TYPE_FLOAT') or (t1 == 'TYPE_FLOAT' and t2 == 'TYPE_INT'):
            return 'TYPE_FLOAT'

        self.error(
            f"Type mismatch{(' in ' + context) if context else ''}: {t1} vs {t2} "
            f"(function '{self.current_function}')."
        )
        return None


    def analyze(self, program):
        # first pass: collect function signatures
        for stmt in program.statements:
            if isinstance(stmt, FuncDef):
                param_types = [p.var_type for p in stmt.params]
                self.declare_function(stmt.func_name, param_types, stmt)

        # analyze functions
        for name, info in self.functions.items():
            self.analyze_function(info['node'], name)

    # analyze top-level statements (implicit __main__)
        self.current_function = '__main__'
        self.push_scope()

        for stmt in program.statements:
            if not isinstance(stmt, FuncDef):
                self.analyze_statement(stmt)

        self.pop_scope()
        self.current_function = None

        return self.errors


    def analyze_function(self, func_node, func_name):
        self.current_function = func_name
        self.push_scope()
        # declare parameters
        for p in func_node.params:
            # p is VarDecl with var_type token string and var_name
            self.declare_var(p.var_name, p.var_type)

        # walk body statements
        for stmt in func_node.body:
            self.analyze_statement(stmt)

        self.pop_scope()
        self.current_function = None

    def analyze_statement(self, stmt):
        # VarDecl
        if isinstance(stmt, VarDecl):
            vtype = stmt.var_type
            # initializer type check
            if stmt.initializer is not None:
                init_t = self.analyze_expression(stmt.initializer)
                if init_t is not None:
                    self.unify(vtype, init_t, f"initializer for '{stmt.var_name}'")
            self.declare_var(stmt.var_name, vtype)
            return

        # Assignment
        if isinstance(stmt, Assignment):
            # identifier is an Identifier node
            if not hasattr(stmt.identifier, 'name'):
                self.error(f"Invalid assignment target in function '{self.current_function}'.")
                return
            name = stmt.identifier.name
            var_t = self.lookup_var(name)
            expr_t = self.analyze_expression(stmt.expression)
            if var_t is not None and expr_t is not None:
                self.unify(var_t, expr_t, f"assignment to '{name}'")
            return

        # Output (bed)
        if isinstance(stmt, OutputStmt):
            _ = self.analyze_expression(stmt.expression)
            return

        # Input (pillow)
        if isinstance(stmt, InputStmt):
            if not hasattr(stmt.identifier, 'name'):
                self.error(f"Invalid input target in function '{self.current_function}'.")
                return
            name = stmt.identifier.name
            if self.lookup_var(name) is None:
                # lookup_var already reported error
                pass
            return

        # If
        if isinstance(stmt, IfStmt):
            cond_t = self.analyze_expression(stmt.condition)
            if cond_t is not None and cond_t != 'TYPE_BOOL':
                self.error(f"If condition must be boolean (found {cond_t}) in function '{self.current_function}'.")
            # analyze blocks in new scope
            self.push_scope()
            for s in stmt.if_block:
                self.analyze_statement(s)
            self.pop_scope()
            if stmt.else_block is not None:
                self.push_scope()
                for s in stmt.else_block:
                    self.analyze_statement(s)
                self.pop_scope()
            return

        # ForLoop
        if isinstance(stmt, ForLoop):
            self.push_scope()
            if stmt.initializer is not None:
                if isinstance(stmt.initializer, VarDecl):
                    self.analyze_statement(stmt.initializer)
                else:
                    _ = self.analyze_expression(stmt.initializer)
            if stmt.condition is not None:
                ctype = self.analyze_expression(stmt.condition)
                if ctype is not None and ctype != 'TYPE_BOOL':
                    self.error(f"For-loop condition must be boolean (found {ctype}) in function '{self.current_function}'.")
            if stmt.increment is not None:
                _ = self.analyze_expression(stmt.increment)
            for s in stmt.body:
                self.analyze_statement(s)
            self.pop_scope()
            return

        # WhileLoop
        if isinstance(stmt, WhileLoop):
            ctype = self.analyze_expression(stmt.condition)
            if ctype is not None and ctype != 'TYPE_BOOL':
                self.error(f"While condition must be boolean (found {ctype}) in function '{self.current_function}'.")
            self.push_scope()
            for s in stmt.body:
                self.analyze_statement(s)
            self.pop_scope()
            return

        # DoWhileLoop
        if isinstance(stmt, DoWhileLoop):
            self.push_scope()
            for s in stmt.body:
                self.analyze_statement(s)
            self.pop_scope()
            ctype = self.analyze_expression(stmt.condition)
            if ctype is not None and ctype != 'TYPE_BOOL':
                self.error(f"Do-while condition must be boolean (found {ctype}) in function '{self.current_function}'.")
            return

        # ReturnStmt
        if isinstance(stmt, ReturnStmt):
            if stmt.expression is None:
                self.set_function_return_value(self.current_function, None)
            else:
                rtype = self.analyze_expression(stmt.expression)
                self.set_function_return_value(self.current_function, rtype)
            return

        # Function call as statement
        if isinstance(stmt, FuncCall):
            _ = self.analyze_expression(stmt)
            return

        # Unknown/unsupported node
        # ignore PauseStmt / Empty or nodes we don't yet support
        return

    def set_function_return_value(self, func_name, rtype):
        if rtype is None:
            # nothing to set
            self.set_function_return(func_name, None)
        else:
            self.set_function_return(func_name, rtype)

    def set_function_return(self, name, rtype):
        # wrapper to set return in self.functions
        if name not in self.functions:
            return
        entry = self.functions[name]
        if entry['return'] is None:
            entry['return'] = rtype
        else:
            if rtype is not None and entry['return'] != rtype:
                # allow int/float promotion
                if {entry['return'], rtype} <= {'TYPE_INT', 'TYPE_FLOAT'}:
                    entry['return'] = 'TYPE_FLOAT'
                else:
                    self.error(f"Inconsistent return types in function '{name}': {entry['return']} vs {rtype}")

    
    def analyze_expression(self, expr):
        if expr is None:
            return None
        if isinstance(expr, Literal):
            return self.literal_to_type(expr.type)
        if isinstance(expr, Identifier):
            return self.lookup_var(expr.name)
        if isinstance(expr, BinaryOp):
            left_t = self.analyze_expression(expr.left)
            right_t = self.analyze_expression(expr.right)
            op = expr.op.value
            if op in ('+', '-', '*', '/', '%'):
                return self.unify(left_t, right_t, "arithmetic")
            if op in ('<', '>', '<=', '>='):
                # numeric comparison -> bool
                res = self.unify(left_t, right_t, "comparison")
                if res is None:
                    return None
                # only numeric comparisons allowed here (TYPE_INT/FLOAT)
                if res in ('TYPE_INT', 'TYPE_FLOAT'):
                    return 'TYPE_BOOL'
                self.error(f"Invalid comparison types in function '{self.current_function}': {left_t} {op} {right_t}")
                return None
            if op in ('==', '!='):
                # equality: allow same types or numeric int/float
                if left_t == right_t:
                    return 'TYPE_BOOL'
                if {left_t, right_t} <= {'TYPE_INT', 'TYPE_FLOAT'}:
                    return 'TYPE_BOOL'
                self.error(f"Invalid equality comparison between {left_t} and {right_t} in function '{self.current_function}'.")
                return None
            # fallback
            return None
        if isinstance(expr, FuncCall):
            fname = expr.identifier.name
            if fname not in self.functions:
                self.error(f"Call to undeclared function '{fname}' in function '{self.current_function}'.")
                return None
            sig = self.functions[fname]
            param_types = sig['params']
            # analyze arg types
            arg_types = [self.analyze_expression(a) for a in expr.args]
            # check count
            if len(arg_types) != len(param_types):
                self.error(f"Function '{fname}' called with wrong number of args in function '{self.current_function}': expected {len(param_types)}, got {len(arg_types)}.")
            else:
                for i, (expected, got) in enumerate(zip(param_types, arg_types)):
                    if expected is None or got is None:
                        continue
                    if expected == got:
                        continue
                    # allow TYPE_INT -> TYPE_FLOAT promotion
                    if expected == 'TYPE_FLOAT' and got == 'TYPE_INT':
                        continue
                    self.error(f"Type mismatch in call to '{fname}' argument {i+1}: expected {expected}, got {got} in function '{self.current_function}'.")
            return sig['return'] or None
        # unknown expression type
        return None
