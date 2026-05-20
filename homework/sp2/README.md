# SL (Simple Language) - 習題 2

## 語言設計目標

SL 是一個簡潔的程式語言，用於展示編譯器與解譯器的實作。設計上參考 p0 語言，但加入條件判斷、迴圈、邏輯運算等實用功能。

## 語言特性

| 特性 | 說明 |
|------|------|
| 型態系統 | 弱型態，僅支援整數 |
| 執行方式 | 直譯器 (AST walk) + 編譯器 (bytecode + 堆疊機 VM) |
| 目標檔格式 | 堆疊機 bytecode |
| 垃圾蒐集 | 無 (僅整數，不需 GC) |
| 記憶體管理 | 區域變數在函數呼叫時配置，返回時釋放 |

## EBNF 語法

```
program       = { top_level }
top_level     = function_def | statement
function_def  = "func" ident "(" [ param_list ] ")" block
param_list    = ident { "," ident }
block         = "{" { statement } "}"
statement     = if_stmt | while_stmt | return_stmt | print_stmt | assign_stmt | expr_stmt
if_stmt       = "if" expression block [ "else" block ]
while_stmt    = "while" expression block
return_stmt   = "return" expression ";"
print_stmt    = "print" expression ";"
assign_stmt   = ident "=" expression ";"
expr_stmt     = expression ";"
expression    = comparison { ("&&" | "||") comparison }
comparison    = addition { ("==" | "!=" | "<" | ">" | "<=" | ">=") addition }
addition      = term { ("+" | "-") term }
term          = factor { ("*" | "/") factor }
factor        = number | ident | "(" expression ")" | call | "-" factor | "!" factor
call          = ident "(" [ arg_list ] ")"
arg_list      = expression { "," expression }
number        = digit { digit }
ident         = letter { letter | digit | "_" }
```

## 支援的功能

- 整數算術運算: `+`, `-`, `*`, `/`
- 比較運算: `==`, `!=`, `<`, `>`, `<=`, `>=`
- 邏輯運算: `&&`, `||`, `!`
- 變數賦值: `x = 42;`
- 條件判斷: `if` / `else`
- 迴圈: `while`
- 函數定義與遞迴呼叫: `func name(params) { ... }`
- 輸出: `print expr;`
- 單行註解: `// ...`

## 執行方式

### 直譯器 (sp2i.py)

```bash
python sp2i.py example.sp2
```

### 編譯器 + VM (sp2c.py)

```bash
python sp2c.py example.sp2
```

## 檔案結構

- `sp2i.py` - 直譯器 (tokenizer → parser → AST → 直接執行)
- `sp2c.py` - 編譯器 + 堆疊機 VM (tokenizer → parser → AST → bytecode → VM 執行)
- `example.sp2` - 範例程式
- `README.md` - 本說明文件
