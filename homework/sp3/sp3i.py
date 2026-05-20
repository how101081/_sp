import sys

class Node: pass

class Program(Node):
    def __init__(self, stmts): self.stmts = stmts

class FuncDef(Node):
    def __init__(self, name, params, body):
        self.name, self.params, self.body = name, params, body

class IfStmt(Node):
    def __init__(self, cond, then_block, else_block):
        self.cond, self.then_block, self.else_block = cond, then_block, else_block

class WhileStmt(Node):
    def __init__(self, cond, body): self.cond, self.body = cond, body

class ForStmt(Node):
    def __init__(self, init, cond, inc, body):
        self.init, self.cond, self.inc, self.body = init, cond, inc, body

class BreakStmt(Node):
    pass

class ContinueStmt(Node):
    pass

class ReturnStmt(Node):
    def __init__(self, expr): self.expr = expr

class PrintStmt(Node):
    def __init__(self, expr): self.expr = expr

class ReadStmt(Node):
    def __init__(self, name): self.name = name

class AssignStmt(Node):
    def __init__(self, name, expr): self.name, self.expr = name, expr

class IndexAssignStmt(Node):
    def __init__(self, name, index, expr): self.name, self.index, self.expr = name, index, expr

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

class ArrayLiteral(Node):
    def __init__(self, elements): self.elements = elements

class IndexExpr(Node):
    def __init__(self, name, index): self.name, self.index = name, index

(TK_EOF, TK_NUM, TK_ID, TK_STR,
 TK_PLUS, TK_MINUS, TK_MUL, TK_DIV,
 TK_LPAREN, TK_RPAREN, TK_LBRACE, TK_RBRACE,
 TK_LBRACKET, TK_RBRACKET,
 TK_SEMI, TK_EQ, TK_ASSIGN, TK_AND, TK_OR, TK_NE,
 TK_LT, TK_GT, TK_LE, TK_GE, TK_NOT, TK_COMMA,
 KW_FUNC, KW_IF, KW_ELSE, KW_WHILE, KW_FOR,
 KW_RETURN, KW_PRINT, KW_READ, KW_BREAK, KW_CONTINUE) = range(36)

keywords = {
    "func": KW_FUNC, "if": KW_IF, "else": KW_ELSE,
    "while": KW_WHILE, "for": KW_FOR,
    "return": KW_RETURN, "print": KW_PRINT,
    "read": KW_READ, "break": KW_BREAK, "continue": KW_CONTINUE,
}

class Token:
    def __init__(self, type, val=""): self.type, self.val = type, val

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
        if c == '/' and pos + 1 < len(src) and src[pos + 1] == '*':
            pos += 2
            while pos + 1 < len(src) and not (src[pos] == '*' and src[pos + 1] == '/'):
                pos += 1
            if pos + 1 < len(src):
                pos += 2
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
        elif c == '[': tokens.append(Token(TK_LBRACKET, c))
        elif c == ']': tokens.append(Token(TK_RBRACKET, c))
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
        if self.peek().type == KW_FUNC:
            return self.func_def()
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
        while self.peek().type != TK_RBRACE and self.peek().type != TK_EOF:
            stmts.append(self.statement())
        self.expect(TK_RBRACE)
        return stmts

    def statement(self):
        if self.peek().type == KW_IF:
            return self.if_stmt()
        if self.peek().type == KW_WHILE:
            return self.while_stmt()
        if self.peek().type == KW_FOR:
            return self.for_stmt()
        if self.peek().type == KW_RETURN:
            return self.return_stmt()
        if self.peek().type == KW_PRINT:
            return self.print_stmt()
        if self.peek().type == KW_READ:
            return self.read_stmt()
        if self.peek().type == KW_BREAK:
            self.next()
            self.expect(TK_SEMI)
            return BreakStmt()
        if self.peek().type == KW_CONTINUE:
            self.next()
            self.expect(TK_SEMI)
            return ContinueStmt()
        if self.peek().type == TK_ID:
            saved = self.pos
            self.next()
            if self.peek().type == TK_ASSIGN:
                self.pos = saved
                return self.assign_stmt()
            if self.peek().type == TK_LBRACKET:
                self.pos = saved
                return self.index_assign_stmt()
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
            elif self.peek().type == KW_IF:
                else_block = [self.if_stmt()]
            else:
                else_block = [self.statement()]
        return IfStmt(cond, then_block, else_block)

    def while_stmt(self):
        self.expect(KW_WHILE)
        cond = self.expression()
        body = self.block()
        return WhileStmt(cond, body)

    def for_stmt(self):
        self.expect(KW_FOR)
        init = None
        cond = None
        inc = None
        if self.peek().type != TK_SEMI:
            if self.peek().type == TK_ID:
                saved = self.pos
                self.next()
                if self.peek().type == TK_ASSIGN:
                    self.pos = saved
                    name = self.expect(TK_ID).val
                    self.expect(TK_ASSIGN)
                    init_expr = self.expression()
                    init = AssignStmt(name, init_expr)
                else:
                    self.pos = saved
                    cond = self.expression()
            else:
                cond = self.expression()
        self.expect(TK_SEMI)
        if self.peek().type != TK_SEMI:
            cond = self.expression()
        self.expect(TK_SEMI)
        if self.peek().type != TK_LBRACE:
            saved = self.pos
            try:
                if self.peek().type == TK_ID:
                    name_tok = self.next()
                    if self.peek().type == TK_ASSIGN:
                        self.pos = saved
                        name = self.expect(TK_ID).val
                        self.expect(TK_ASSIGN)
                        inc_expr = self.expression()
                        inc = AssignStmt(name, inc_expr)
                    else:
                        self.pos = saved
                        inc = self.expression()
                else:
                    self.pos = saved
                    inc = self.expression()
            except Exception:
                self.pos = saved
        body = self.block()
        return ForStmt(init, cond, inc, body)

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

    def read_stmt(self):
        self.expect(KW_READ)
        name = self.expect(TK_ID).val
        self.expect(TK_SEMI)
        return ReadStmt(name)

    def assign_stmt(self):
        name = self.expect(TK_ID).val
        self.expect(TK_ASSIGN)
        expr = self.expression()
        self.expect(TK_SEMI)
        return AssignStmt(name, expr)

    def index_assign_stmt(self):
        name = self.expect(TK_ID).val
        self.expect(TK_LBRACKET)
        index = self.expression()
        self.expect(TK_RBRACKET)
        self.expect(TK_ASSIGN)
        expr = self.expression()
        self.expect(TK_SEMI)
        return IndexAssignStmt(name, index, expr)

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
        if self.peek().type == TK_LBRACKET:
            self.next()
            elements = []
            if self.peek().type != TK_RBRACKET:
                elements.append(self.expression())
                while self.peek().type == TK_COMMA:
                    self.next()
                    elements.append(self.expression())
            self.expect(TK_RBRACKET)
            return ArrayLiteral(elements)
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
            if self.peek().type == TK_LBRACKET:
                self.next()
                index = self.expression()
                self.expect(TK_RBRACKET)
                return IndexExpr(name, index)
            return Var(name)
        raise Exception(f"Unexpected token: {self.peek().val} (type {self.peek().type})")

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

class Interpreter:
    def __init__(self):
        self.globals = {}
        self.functions = {}
        self._break_flag = False
        self._continue_flag = False

    def run(self, node):
        if isinstance(node, Program):
            for stmt in node.stmts:
                self.run(stmt)
        elif isinstance(node, FuncDef):
            self.functions[node.name] = node
        elif isinstance(node, IfStmt):
            if self.is_truthy(self.run_expr(node.cond)):
                for s in node.then_block:
                    self.run(s)
                    if self._break_flag or self._continue_flag:
                        break
            else:
                for s in node.else_block:
                    self.run(s)
                    if self._break_flag or self._continue_flag:
                        break
        elif isinstance(node, WhileStmt):
            while self.is_truthy(self.run_expr(node.cond)):
                for s in node.body:
                    self.run(s)
                    if self._break_flag:
                        self._break_flag = False
                        return
                    if self._continue_flag:
                        self._continue_flag = False
                        break
        elif isinstance(node, ForStmt):
            if node.init:
                if isinstance(node.init, AssignStmt):
                    self.globals[node.init.name] = self.run_expr(node.init.expr)
                else:
                    self.run(node.init)
            while True:
                if node.cond and not self.is_truthy(self.run_expr(node.cond)):
                    break
                for s in node.body:
                    self.run(s)
                    if self._break_flag:
                        self._break_flag = False
                        return
                    if self._continue_flag:
                        self._continue_flag = False
                        break
                if node.inc:
                    if isinstance(node.inc, AssignStmt):
                        self.globals[node.inc.name] = self.run_expr(node.inc.expr)
                    else:
                        self.run(node.inc)
        elif isinstance(node, BreakStmt):
            self._break_flag = True
        elif isinstance(node, ContinueStmt):
            self._continue_flag = True
        elif isinstance(node, ReturnStmt):
            raise ReturnException(self.run_expr(node.expr))
        elif isinstance(node, PrintStmt):
            print(self.run_expr(node.expr))
        elif isinstance(node, ReadStmt):
            try:
                self.globals[node.name] = int(input())
            except ValueError:
                self.globals[node.name] = 0
        elif isinstance(node, AssignStmt):
            self.globals[node.name] = self.run_expr(node.expr)
        elif isinstance(node, IndexAssignStmt):
            arr = self.globals.get(node.name, [])
            if not isinstance(arr, list):
                raise Exception(f"Cannot index non-array: {node.name}")
            idx = self.run_expr(node.index)
            arr[idx] = self.run_expr(node.expr)
        elif isinstance(node, ExprStmt):
            self.run_expr(node.expr)

    def run_expr(self, node, env=None):
        if env is None: env = self.globals
        if isinstance(node, Num):
            return int(node.val)
        if isinstance(node, Str):
            return node.val
        if isinstance(node, Var):
            if node.name in env:
                return env[node.name]
            raise Exception(f"Undefined variable: {node.name}")
        if isinstance(node, ArrayLiteral):
            return [self.run_expr(e, env) for e in node.elements]
        if isinstance(node, IndexExpr):
            arr = self.run_expr(Var(node.name), env)
            idx = self.run_expr(node.index, env)
            if isinstance(arr, str):
                return arr[idx]
            return arr[idx]
        if isinstance(node, BinOp):
            l = self.run_expr(node.left, env)
            r = self.run_expr(node.right, env)
            if node.op == "+":
                if isinstance(l, str) or isinstance(r, str):
                    return str(l) + str(r)
                if isinstance(l, list) and isinstance(r, list):
                    return l + r
                return l + r
            if node.op == "-": return l - r
            if node.op == "*": return l * r
            if node.op == "/":
                if r == 0: raise Exception("Division by zero")
                return int(l / r)
            if node.op == "==": return 1 if l == r else 0
            if node.op == "!=": return 1 if l != r else 0
            if node.op == "<": return 1 if l < r else 0
            if node.op == ">": return 1 if l > r else 0
            if node.op == "<=": return 1 if l <= r else 0
            if node.op == ">=": return 1 if l >= r else 0
            if node.op == "&&": return 1 if (self.is_truthy(l) and self.is_truthy(r)) else 0
            if node.op == "||": return 1 if (self.is_truthy(l) or self.is_truthy(r)) else 0
        if isinstance(node, UnaryOp):
            v = self.run_expr(node.expr, env)
            if node.op == "-": return -v
            if node.op == "!": return 0 if self.is_truthy(v) else 1
        if isinstance(node, Call):
            func = self.functions.get(node.name)
            if not func:
                raise Exception(f"Undefined function: {node.name}")
            args = [self.run_expr(a, env) for a in node.args]
            new_env = dict(zip(func.params, args))
            try:
                for s in func.body:
                    self.run_in_env(s, new_env)
            except ReturnException as e:
                return e.value
            return 0
        raise Exception(f"Unknown expr: {type(node)}")

    def run_in_env(self, node, env):
        if isinstance(node, IfStmt):
            if self.is_truthy(self.run_expr(node.cond, env)):
                for s in node.then_block:
                    self.run_in_env(s, env)
                    if self._break_flag or self._continue_flag:
                        break
            else:
                for s in node.else_block:
                    self.run_in_env(s, env)
                    if self._break_flag or self._continue_flag:
                        break
        elif isinstance(node, WhileStmt):
            while self.is_truthy(self.run_expr(node.cond, env)):
                for s in node.body:
                    self.run_in_env(s, env)
                    if self._break_flag:
                        self._break_flag = False
                        return
                    if self._continue_flag:
                        self._continue_flag = False
                        break
        elif isinstance(node, ForStmt):
            if node.init:
                if isinstance(node.init, AssignStmt):
                    env[node.init.name] = self.run_expr(node.init.expr, env)
                else:
                    self.run_in_env(node.init, env)
            while True:
                if node.cond and not self.is_truthy(self.run_expr(node.cond, env)):
                    break
                for s in node.body:
                    self.run_in_env(s, env)
                    if self._break_flag:
                        self._break_flag = False
                        return
                    if self._continue_flag:
                        self._continue_flag = False
                        break
                if node.inc:
                    if isinstance(node.inc, AssignStmt):
                        env[node.inc.name] = self.run_expr(node.inc.expr, env)
                    else:
                        self.run_in_env(node.inc, env)
        elif isinstance(node, BreakStmt):
            self._break_flag = True
        elif isinstance(node, ContinueStmt):
            self._continue_flag = True
        elif isinstance(node, ReturnStmt):
            raise ReturnException(self.run_expr(node.expr, env))
        elif isinstance(node, PrintStmt):
            print(self.run_expr(node.expr, env))
        elif isinstance(node, ReadStmt):
            try:
                env[node.name] = int(input())
            except ValueError:
                env[node.name] = 0
        elif isinstance(node, AssignStmt):
            env[node.name] = self.run_expr(node.expr, env)
        elif isinstance(node, IndexAssignStmt):
            arr = env.get(node.name, [])
            if not isinstance(arr, list):
                raise Exception(f"Cannot index non-array: {node.name}")
            idx = self.run_expr(node.index, env)
            arr[idx] = self.run_expr(node.expr, env)
        elif isinstance(node, ExprStmt):
            self.run_expr(node.expr, env)

    def is_truthy(self, val):
        if isinstance(val, str): return True
        if isinstance(val, list): return True
        return val != 0

class ReturnException(Exception):
    def __init__(self, value): self.value = value

def main():
    if len(sys.argv) < 2:
        print("Usage: python sp3i.py <file.sp3>")
        sys.exit(1)
    with open(sys.argv[1]) as f:
        src = f.read()
    tokens = tokenize(src)
    parser = Parser(tokens)
    ast = parser.parse()
    interp = Interpreter()
    interp.run(ast)

if __name__ == "__main__":
    main()
