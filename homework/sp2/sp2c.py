import sys

# ========== Bytecode Instructions ==========
PUSH = 0
POP = 1
ADD = 2
SUB = 3
MUL = 4
DIV = 5
EQ = 6
NE = 7
LT = 8
GT = 9
LE = 10
GE = 11
JMP = 12
JZ = 13
CALL = 14
RET = 15
SET = 16
GET = 17
PRINT = 18
HALT = 19
NOT = 20

op_names = [
    "PUSH", "POP", "ADD", "SUB", "MUL", "DIV", "EQ", "NE",
    "LT", "GT", "LE", "GE", "JMP", "JZ", "CALL", "RET",
    "SET", "GET", "PRINT", "HALT", "NOT",
]

# ========== Token Types ==========
(TK_EOF, TK_NUM, TK_ID, TK_STR,
 TK_PLUS, TK_MINUS, TK_MUL, TK_DIV,
 TK_LPAREN, TK_RPAREN, TK_LBRACE, TK_RBRACE,
 TK_SEMI, TK_EQ, TK_ASSIGN, TK_AND, TK_OR, TK_NE,
 TK_LT, TK_GT, TK_LE, TK_GE, TK_NOT, TK_COMMA,
 KW_FUNC, KW_IF, KW_ELSE, KW_WHILE, KW_RETURN, KW_PRINT) = range(30)

keywords = {
    "func": KW_FUNC, "if": KW_IF, "else": KW_ELSE,
    "while": KW_WHILE, "return": KW_RETURN, "print": KW_PRINT,
}

class Token:
    def __init__(self, type, val=""): self.type, self.val = type, val

# ========== Tokenizer ==========
def tokenize(src):
    tokens = []
    pos = 0
    while pos < len(src):
        c = src[pos]
        if c in " \t\r\n":
            pos += 1
            continue
        if c == '/' and pos + 1 < len(src) and src[pos + 1] == '/':
            while pos < len(src) and src[pos] != '\n':
                pos += 1
            continue
        if c.isdigit():
            start = pos
            while pos < len(src) and src[pos].isdigit():
                pos += 1
            tokens.append(Token(TK_NUM, src[start:pos]))
            continue
        if c.isalpha() or c == '_':
            start = pos
            while pos < len(src) and (src[pos].isalnum() or src[pos] == '_'):
                pos += 1
            word = src[start:pos]
            kw = keywords.get(word)
            tokens.append(Token(kw if kw else TK_ID, word))
            continue
        if c == '"':
            pos += 1
            start = pos
            while pos < len(src) and src[pos] != '"':
                pos += 1
            tokens.append(Token(TK_STR, src[start:pos]))
            pos += 1
            continue
        pos += 1
        if c == '+': tokens.append(Token(TK_PLUS, c))
        elif c == '-': tokens.append(Token(TK_MINUS, c))
        elif c == '*': tokens.append(Token(TK_MUL, c))
        elif c == '/': tokens.append(Token(TK_DIV, c))
        elif c == '(': tokens.append(Token(TK_LPAREN, c))
        elif c == ')': tokens.append(Token(TK_RPAREN, c))
        elif c == '{': tokens.append(Token(TK_LBRACE, c))
        elif c == '}': tokens.append(Token(TK_RBRACE, c))
        elif c == ';': tokens.append(Token(TK_SEMI, c))
        elif c == ',':
            tokens.append(Token(TK_COMMA, c))
        elif c == '=':
            if pos < len(src) and src[pos] == '=':
                pos += 1
                tokens.append(Token(TK_EQ, "=="))
            else:
                tokens.append(Token(TK_ASSIGN, c))
        elif c == '!':
            if pos < len(src) and src[pos] == '=':
                pos += 1
                tokens.append(Token(TK_NE, "!="))
            else:
                tokens.append(Token(TK_NOT, c))
        elif c == '<':
            if pos < len(src) and src[pos] == '=':
                pos += 1
                tokens.append(Token(TK_LE, "<="))
            else:
                tokens.append(Token(TK_LT, c))
        elif c == '>':
            if pos < len(src) and src[pos] == '=':
                pos += 1
                tokens.append(Token(TK_GE, ">="))
            else:
                tokens.append(Token(TK_GT, c))
        elif c == '&' and pos < len(src) and src[pos] == '&':
            pos += 1
            tokens.append(Token(TK_AND, "&&"))
        elif c == '|' and pos < len(src) and src[pos] == '|':
            pos += 1
            tokens.append(Token(TK_OR, "||"))
        else:
            raise Exception(f"Unexpected char: '{c}' at pos {pos}")
    tokens.append(Token(TK_EOF, "EOF"))
    return tokens

# ========== AST Nodes ==========
class Node: pass
class Program(Node):
    def __init__(self, stmts): self.stmts = stmts
class FuncDef(Node):
    def __init__(self, name, params, body): self.name, self.params, self.body = name, params, body
class IfStmt(Node):
    def __init__(self, cond, then_block, else_block): self.cond, self.then_block, self.else_block = cond, then_block, else_block
class WhileStmt(Node):
    def __init__(self, cond, body): self.cond, self.body = cond, body
class ReturnStmt(Node):
    def __init__(self, expr): self.expr = expr
class PrintStmt(Node):
    def __init__(self, expr): self.expr = expr
class AssignStmt(Node):
    def __init__(self, name, expr): self.name, self.expr = name, expr
class ExprStmt(Node):
    def __init__(self, expr): self.expr = expr
class BinOp(Node):
    def __init__(self, op, left, right): self.op, self.left, self.right = op, left, right
class UnaryOp(Node):
    def __init__(self, op, expr): self.op, self.expr = op, expr
class Call(Node):
    def __init__(self, name, args): self.name, self.args = name, args
class Num(Node):
    def __init__(self, val): self.val = int(val)
class Var(Node):
    def __init__(self, name): self.name = name
class Str(Node):
    def __init__(self, val): self.val = val

# ========== Parser ==========
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos]

    def next(self):
        t = self.tokens[self.pos]
        self.pos += 1
        return t

    def expect(self, type, msg=""):
        if self.peek().type != type:
            raise Exception(f"{msg} expected {type}, got {self.peek().val}")
        return self.next()

    def parse(self):
        stmts = []
        while self.peek().type != TK_EOF:
            stmts.append(self.top_level())
        return Program(stmts)

    def top_level(self):
        if self.peek().type == KW_FUNC: return self.func_def()
        return self.statement()

    def func_def(self):
        self.expect(KW_FUNC)
        name = self.expect(TK_ID).val
        self.expect(TK_LPAREN)
        params = []
        if self.peek().type != TK_RPAREN:
            params.append(self.expect(TK_ID).val)
            while self.peek().type == TK_COMMA:
                self.next()
                params.append(self.expect(TK_ID).val)
        self.expect(TK_RPAREN)
        body = self.block()
        return FuncDef(name, params, body)

    def block(self):
        self.expect(TK_LBRACE)
        stmts = []
        while self.peek().type not in (TK_RBRACE, TK_EOF):
            stmts.append(self.statement())
        self.expect(TK_RBRACE)
        return stmts

    def statement(self):
        if self.peek().type == KW_IF: return self.if_stmt()
        if self.peek().type == KW_WHILE: return self.while_stmt()
        if self.peek().type == KW_RETURN: return self.return_stmt()
        if self.peek().type == KW_PRINT: return self.print_stmt()
        if self.peek().type == TK_ID:
            saved = self.pos
            self.next()
            if self.peek().type == TK_ASSIGN:
                self.pos = saved
                return self.assign_stmt()
            self.pos = saved
        return ExprStmt(self.expression())

    def if_stmt(self):
        self.expect(KW_IF)
        cond = self.expression()
        then_block = self.block()
        else_block = []
        if self.peek().type == KW_ELSE:
            self.next()
            if self.peek().type == TK_LBRACE:
                else_block = self.block()
            else:
                else_block = [self.if_stmt()]
        return IfStmt(cond, then_block, else_block)

    def while_stmt(self):
        self.expect(KW_WHILE)
        cond = self.expression()
        body = self.block()
        return WhileStmt(cond, body)

    def return_stmt(self):
        self.expect(KW_RETURN)
        expr = self.expression()
        self.expect(TK_SEMI)
        return ReturnStmt(expr)

    def print_stmt(self):
        self.expect(KW_PRINT)
        expr = self.expression()
        self.expect(TK_SEMI)
        return PrintStmt(expr)

    def assign_stmt(self):
        name = self.expect(TK_ID).val
        self.expect(TK_ASSIGN)
        expr = self.expression()
        self.expect(TK_SEMI)
        return AssignStmt(name, expr)

    def expression(self):
        left = self.comparison()
        while self.peek().type in (TK_AND, TK_OR):
            op = "&&" if self.peek().type == TK_AND else "||"
            self.next()
            right = self.comparison()
            left = BinOp(op, left, right)
        return left

    def comparison(self):
        left = self.addition()
        typemap = {TK_EQ: "==", TK_NE: "!=", TK_LT: "<", TK_GT: ">", TK_LE: "<=", TK_GE: ">="}
        while self.peek().type in typemap:
            op = typemap[self.peek().type]
            self.next()
            right = self.addition()
            left = BinOp(op, left, right)
        return left

    def addition(self):
        left = self.term()
        while self.peek().type in (TK_PLUS, TK_MINUS):
            op = "+" if self.peek().type == TK_PLUS else "-"
            self.next()
            right = self.term()
            left = BinOp(op, left, right)
        return left

    def term(self):
        left = self.factor()
        while self.peek().type in (TK_MUL, TK_DIV):
            op = "*" if self.peek().type == TK_MUL else "/"
            self.next()
            right = self.factor()
            left = BinOp(op, left, right)
        return left

    def factor(self):
        if self.peek().type == TK_NUM:
            return Num(self.next().val)
        if self.peek().type == TK_STR:
            return Str(self.next().val)
        if self.peek().type == TK_MINUS:
            self.next()
            return UnaryOp("-", self.factor())
        if self.peek().type == TK_NOT:
            self.next()
            return UnaryOp("!", self.factor())
        if self.peek().type == TK_LPAREN:
            self.next()
            expr = self.expression()
            self.expect(TK_RPAREN)
            return expr
        if self.peek().type == TK_ID:
            name = self.next().val
            if self.peek().type == TK_LPAREN:
                return self.call(name)
            return Var(name)
        raise Exception(f"Unexpected token: {self.peek().val}")

    def call(self, name):
        self.expect(TK_LPAREN)
        args = []
        if self.peek().type != TK_RPAREN:
            args.append(self.expression())
            while self.peek().type == TK_COMMA:
                self.next()
                args.append(self.expression())
        self.expect(TK_RPAREN)
        return Call(name, args)

# ========== Bytecode Compiler ==========
class Compiler:
    def __init__(self):
        self.bytecode = []
        self.functions = {}
        self.func_stack = []
        self.label_counter = 0

    def new_label(self):
        self.label_counter += 1
        return f"L{self.label_counter}"

    def emit(self, op, arg=None):
        self.bytecode.append((op, arg))

    def compile(self, node):
        if isinstance(node, Program):
            return self.compile_program(node)
        else:
            raise Exception(f"Cannot compile {type(node)} at top level")

    def compile_program(self, node):
        for stmt in node.stmts:
            if isinstance(stmt, FuncDef):
                self.functions[stmt.name] = stmt

        for stmt in node.stmts:
            if not isinstance(stmt, FuncDef):
                self.compile_stmt(stmt)
        self.emit(HALT)

        for name, func in self.functions.items():
            self.functions[name] = self.compile_func(func)

        return self.bytecode

    def compile_func(self, node):
        saved = self.bytecode
        self.bytecode = []
        self.label_positions = {}
        self.func_stack.append(node.name)

        self.emit("FUNC_HEAD", {"name": node.name, "params": len(node.params)})

        for stmt in node.body:
            self.compile_stmt(stmt)

        self.emit(PUSH, 0)
        self.emit(RET)

        func_data = {
            "name": node.name,
            "param_names": node.params,
            "params": len(node.params),
            "bytecode": self.bytecode,
            "label_positions": self.label_positions,
        }

        self.bytecode = saved
        self.func_stack.pop()
        return func_data

    def compile_stmt(self, node):
        if isinstance(node, IfStmt):
            end_label = self.new_label()
            else_label = self.new_label()
            self.compile_expr(node.cond)
            self.emit(JZ, else_label)
            for s in node.then_block:
                self.compile_stmt(s)
            self.emit(JMP, end_label)
            self.emit("LABEL", else_label)
            for s in node.else_block:
                self.compile_stmt(s)
            self.emit("LABEL", end_label)
        elif isinstance(node, WhileStmt):
            start_label = self.new_label()
            end_label = self.new_label()
            self.emit("LABEL", start_label)
            self.compile_expr(node.cond)
            self.emit(JZ, end_label)
            for s in node.body:
                self.compile_stmt(s)
            self.emit(JMP, start_label)
            self.emit("LABEL", end_label)
        elif isinstance(node, ReturnStmt):
            self.compile_expr(node.expr)
            self.emit(RET)
        elif isinstance(node, PrintStmt):
            self.compile_expr(node.expr)
            self.emit(PRINT)
        elif isinstance(node, AssignStmt):
            self.compile_expr(node.expr)
            self.emit(SET, node.name)
        elif isinstance(node, ExprStmt):
            self.compile_expr(node.expr)
            self.emit(POP)

    def compile_expr(self, node):
        if isinstance(node, Num):
            self.emit(PUSH, node.val)
        elif isinstance(node, Str):
            self.emit(PUSH, node.val)
        elif isinstance(node, Var):
            self.emit(GET, node.name)
        elif isinstance(node, BinOp):
            self.compile_expr(node.left)
            self.compile_expr(node.right)
            if node.op == "+": self.emit(ADD)
            elif node.op == "-": self.emit(SUB)
            elif node.op == "*": self.emit(MUL)
            elif node.op == "/": self.emit(DIV)
            elif node.op == "==": self.emit(EQ)
            elif node.op == "!=": self.emit(NE)
            elif node.op == "<": self.emit(LT)
            elif node.op == ">": self.emit(GT)
            elif node.op == "<=": self.emit(LE)
            elif node.op == ">=": self.emit(GE)
            elif node.op == "&&":
                false_l = self.new_label()
                end_l = self.new_label()
                self.emit(JZ, false_l)
                self.emit(POP)
                self.compile_expr(node.right)
                self.emit(JMP, end_l)
                self.emit("LABEL", false_l)
                self.emit(POP)
                self.emit(PUSH, 0)
                self.emit("LABEL", end_l)
            elif node.op == "||":
                true_l = self.new_label()
                end_l = self.new_label()
                self.emit(JZ, true_l)
                self.emit(POP)
                self.emit(PUSH, 1)
                self.emit(JMP, end_l)
                self.emit("LABEL", true_l)
                self.emit(POP)
                self.compile_expr(node.right)
                self.emit("LABEL", end_l)
        elif isinstance(node, UnaryOp):
            if node.op == "-":
                self.emit(PUSH, 0)
                self.compile_expr(node.expr)
                self.emit(SUB)
            elif node.op == "!":
                self.compile_expr(node.expr)
                self.emit(NOT)
        elif isinstance(node, Call):
            self.compile_call(node)
        else:
            raise Exception(f"Cannot compile expr: {type(node)}")

    def compile_call(self, node):
        for arg in node.args:
            self.compile_expr(arg)
        self.emit(CALL, node.name)

# ========== Stack Virtual Machine ==========
class VM:
    def __init__(self, bytecode, functions):
        self.bytecode = bytecode
        self.functions = functions
        self.stack = []
        self.pc = 0
        self.call_stack = []
        self.vars = {}
        self.output = []

    def run(self):
        resolved_bc, labels = self.resolve_bytecode(self.bytecode, {})
        self.main_bc = resolved_bc
        self.main_labels = labels
        self.pc = 0
        self.vars = {}
        self.stack = []
        self.call_stack = []

        while self.pc < len(self.main_bc):
            instr = self.main_bc[self.pc]
            self.pc += 1
            self.execute(instr)

    def resolve_bytecode(self, bc, labels):
        resolved = []
        pos = 0
        for op, arg in bc:
            if op == "LABEL":
                labels[arg] = pos
            else:
                resolved.append((op, arg))
                pos += 1
        for i in range(len(resolved)):
            op, arg = resolved[i]
            if op in (JMP, JZ, CALL) and isinstance(arg, str) and arg in labels:
                resolved[i] = (op, labels[arg])
        return resolved, labels

    def execute(self, instr):
        op, arg = instr
        if op == PUSH:
            self.stack.append(arg)
        elif op == POP:
            self.stack.pop()
        elif op == ADD:
            b, a = self.stack.pop(), self.stack.pop()
            if isinstance(a, str) or isinstance(b, str):
                self.stack.append(str(a) + str(b))
            else:
                self.stack.append(a + b)
        elif op == SUB:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a - b)
        elif op == MUL:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a * b)
        elif op == DIV:
            b, a = self.stack.pop(), self.stack.pop()
            if b == 0: raise Exception("Division by zero")
            self.stack.append(int(a / b))
        elif op == EQ:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(1 if a == b else 0)
        elif op == NE:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(1 if a != b else 0)
        elif op == LT:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(1 if a < b else 0)
        elif op == GT:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(1 if a > b else 0)
        elif op == LE:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(1 if a <= b else 0)
        elif op == GE:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(1 if a >= b else 0)
        elif op == NOT:
            a = self.stack.pop()
            self.stack.append(1 if a == 0 else 0)
        elif op == JMP:
            self.pc = arg
        elif op == JZ:
            if self.stack.pop() == 0:
                self.pc = arg
        elif op == CALL:
            func_name = arg
            func = self.functions.get(func_name)
            if not func:
                raise Exception(f"Undefined function: {func_name}")
            func_bc = func["bytecode"]
            resolved_bc, _ = self.resolve_bytecode(func_bc, {})
            param_names = func.get("param_names", [])
            param_count = func["params"]
            args_rev = []
            for _ in range(param_count):
                args_rev.insert(0, self.stack.pop())
            self.call_stack.append({
                "pc": self.pc,
                "bc": self.main_bc,
                "vars": self.vars.copy(),
            })
            self.vars = {}
            for i, name in enumerate(param_names):
                self.vars[name] = args_rev[i] if i < len(args_rev) else 0
            self.main_bc = resolved_bc
            self.pc = 0
        elif op == RET:
            ret_val = self.stack.pop() if self.stack else 0
            if self.call_stack:
                saved = self.call_stack.pop()
                self.pc = saved["pc"]
                self.main_bc = saved["bc"]
                self.vars = saved["vars"]
                self.stack.append(ret_val)
            else:
                self.stack = [ret_val]
        elif op == SET:
            self.vars[arg] = self.stack.pop()
        elif op == GET:
            val = self.vars.get(arg, 0)
            self.stack.append(val)
        elif op == PRINT:
            val = self.stack.pop()
            print(val)
            self.output.append(val)
        elif op == HALT:
            self.pc = len(self.main_bc)

def main():
    if len(sys.argv) < 2:
        print("Usage: python sp2c.py <file.sp2>")
        sys.exit(1)
    with open(sys.argv[1]) as f:
        src = f.read()
    tokens = tokenize(src)
    parser = Parser(tokens)
    ast = parser.parse()
    compiler = Compiler()
    bc = compiler.compile(ast)

    print("=== Bytecode ===")
    for i, (op, arg) in enumerate(bc):
        if isinstance(op, str) and op == "LABEL":
            print(f"  {arg}:")
        elif isinstance(op, str) and op == "FUNC_HEAD":
            print(f"\n--- Function: {arg['name']} (params: {arg['params']}) ---")
        else:
            op_name = op_names[op] if isinstance(op, int) else str(op)
            arg_str = f" {arg}" if arg is not None else ""
            print(f"  {i:4d}: {op_name}{arg_str}")

    print("\n=== VM Execution ===")
    vm = VM(bc, compiler.functions)
    vm.run()
    print("=== Done ===")

if __name__ == "__main__":
    main()
