import sys

try:
    
    from scanner2 import tokenize, Token 
except ImportError:
    print("Error: Could not find 'scanner2.py'.")
    print("Make sure it's in the same directory as this file.")
    sys.exit()

try:
   
    from parser import (
        Parser, ASTNode, Program, FuncDef, VarDecl, IfStmt, OutputStmt, 
        InputStmt, ForLoop, WhileLoop, DoWhileLoop, ReturnStmt, PauseStmt, 
        Empty, Assignment, FuncCall, BinaryOp, Literal, Identifier
    )
except ImportError:
    print("Error: Could not find 'zzzleep_parser.py'.")
    print("Make sure it's in the same directory as this file.")
    sys.exit()




class ASTVisualizer:
   
    def __init__(self):
        self.output = ""

    def _visit(self, node, line_prefix, child_prefix):   
        method_name = f'visit_{node.__class__.__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        visitor(node, line_prefix, child_prefix)

    def _visit_child_list(self, children, parent_child_prefix):
        for i, child in enumerate(children):
            is_last = (i == len(children) - 1)
            line_p = "└── " if is_last else "├── "
            child_p = "    " if is_last else "│   "
            self._visit(child, parent_child_prefix + line_p, parent_child_prefix + child_p)

    def _visit_child(self, child, is_last, parent_child_prefix):
        if child:
            line_p = "└── " if is_last else "├── "
            child_p = "    " if is_last else "│   "
            self._visit(child, parent_child_prefix + line_p, parent_child_prefix + child_p)

    def visualize(self, node: ASTNode):
        self.output = ""
        self._visit(node, "", "")
        return self.output

    def generic_visit(self, node, line_prefix, child_prefix):
        self.output += f"{line_prefix}{node.__class__.__name__}\n"

    def visit_Program(self, node, line_prefix, child_prefix):
        self.output += f"{line_prefix}Program\n"
        self._visit_child_list(node.statements, child_prefix)

    def visit_FuncDef(self, node, line_prefix, child_prefix):
        self.output += f"{line_prefix}FuncDef (name='{node.func_name}')\n"
        

        if node.params:
            params_line = child_prefix + "├── (params)\n"
            params_child = child_prefix + "│   "
            self.output += params_line
            self._visit_child_list(node.params, params_child)
        

        body_line = child_prefix + "└── (body)\n"
        body_child = child_prefix + "    "
        self.output += body_line
        self._visit_child_list(node.body, body_child)

    def visit_VarDecl(self, node, line_prefix, child_prefix):
        self.output += f"{line_prefix}VarDecl (type={node.var_type}, name='{node.var_name}')\n"
        if node.initializer:
            self._visit(node.initializer, child_prefix + "└── ", child_prefix + "    ")

    def visit_IfStmt(self, node, line_prefix, child_prefix):
        self.output += f"{line_prefix}IfStmt\n"
        
       
        self.output += f"{child_prefix}├── (condition)\n"
        self._visit(node.condition, child_prefix + "│   └── ", child_prefix + "│       ")
        
       
        if node.else_block:
            self.output += f"{child_prefix}├── (if_block)\n"
            self._visit_child_list(node.if_block, child_prefix + "│   ")
            
            self.output += f"{child_prefix}└── (else_block)\n"
            self._visit_child_list(node.else_block, child_prefix + "    ")
        else:
            self.output += f"{child_prefix}└── (if_block)\n"
            self._visit_child_list(node.if_block, child_prefix + "    ")

    def visit_OutputStmt(self, node, line_prefix, child_prefix):
        self.output += f"{line_prefix}OutputStmt\n"
        self._visit(node.expression, child_prefix + "└── ", child_prefix + "    ")

    def visit_InputStmt(self, node, line_prefix, child_prefix):
        self.output += f"{line_prefix}InputStmt\n"
        self._visit(node.identifier, child_prefix + "└── ", child_prefix + "    ")

    def visit_ForLoop(self, node, line_prefix, child_prefix):
        self.output += f"{line_prefix}ForLoop\n"
        self._visit_child(node.initializer, False, child_prefix + "├── (init) ")
        self._visit_child(node.condition, False, child_prefix + "├── (cond) ")
        self._visit_child(node.increment, True, child_prefix + "└── (inc)  ")
        
        self.output += f"{child_prefix}    (body)\n"
        self._visit_child_list(node.body, child_prefix + "    ")

    def visit_WhileLoop(self, node, line_prefix, child_prefix):
        self.output += f"{line_prefix}WhileLoop\n"
        self.output += f"{child_prefix}├── (condition)\n"
        self._visit(node.condition, child_prefix + "│   └── ", child_prefix + "│       ")
        self.output += f"{child_prefix}└── (body)\n"
        self._visit_child_list(node.body, child_prefix + "    ")

    def visit_DoWhileLoop(self, node, line_prefix, child_prefix):
        self.output += f"{line_prefix}DoWhileLoop\n"
        self.output += f"{child_prefix}├── (body)\n"
        self._visit_child_list(node.body, child_prefix + "│   ")
        self.output += f"{child_prefix}└── (condition)\n"
        self._visit(node.condition, child_prefix + "    └── ", child_prefix + "        ")

    def visit_ReturnStmt(self, node, line_prefix, child_prefix):
        self.output += f"{line_prefix}ReturnStmt\n"
        if node.expression:
            self._visit(node.expression, child_prefix + "└── ", child_prefix + "    ")

    def visit_PauseStmt(self, node, line_prefix, child_prefix):
        self.output += f"{line_prefix}PauseStmt\n"

    def visit_Empty(self, node, line_prefix, child_prefix):
        self.output += f"{line_prefix}Empty\n"

    def visit_Assignment(self, node, line_prefix, child_prefix):
        self.output += f"{line_prefix}Assignment\n"
        self._visit(node.identifier, child_prefix + "├── ", child_prefix + "│   ")
        self._visit(node.expression, child_prefix + "└── ", child_prefix + "    ")

    def visit_FuncCall(self, node, line_prefix, child_prefix):
        self.output += f"{line_prefix}FuncCall\n"
        self._visit(node.identifier, child_prefix + "├── ", child_prefix + "│   ")
        if node.args:
            self.output += f"{child_prefix}└── (args)\n"
            self._visit_child_list(node.args, child_prefix + "    ")

    def visit_BinaryOp(self, node, line_prefix, child_prefix):
        self.output += f"{line_prefix}BinaryOp (op='{node.op.value}')\n"
        self._visit(node.left, child_prefix + "├── ", child_prefix + "│   ")
        self._visit(node.right, child_prefix + "└── ", child_prefix + "    ")

    def visit_Literal(self, node, line_prefix, child_prefix):
        self.output += f"{line_prefix}Literal (value={node.value})\n"

    def visit_Identifier(self, node, line_prefix, child_prefix):
        self.output += f"{line_prefix}Identifier (name='{node.name}')\n"



if __name__ == "__main__":
    
    file_to_parse = "examplescanner2.txt"

   
    print(f"--- 1. Lexing file: '{file_to_parse}' ---")
    tokens = tokenize(file_to_parse)
    if not tokens:
        print("Lexing failed.")
        sys.exit()
    print(f"Successfully lexed {len(tokens)} tokens.")

   
    print(f"\n--- 2. Parsing tokens into AST ---")
    parser = Parser(tokens)
    try:
        ast = parser.parse()
        print("Parsing successful!")
        print(f"\n--- 3. Visual AST Tree ---")
        visualizer = ASTVisualizer()
        tree_output = visualizer.visualize(ast)
        print(tree_output)
        
    except SyntaxError as e:
        print(f"\nParse Failed: {e}")