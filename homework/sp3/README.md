# SL3 - 習題 3

## 專案概述

SL3 是從 [sp2](../sp2) 的 SL (Simple Language) 延伸而來的進階版本，使用 AI 工具 (OpenCode + BigPickle) 輔助開發。

## 新增功能 (vs sp2)

| 功能 | 說明 |
|------|------|
| 陣列 | `arr = [1, 2, 3];` `x = arr[0];` `arr[1] = 42;` |
| For 迴圈 | `for i = 0; i < 10; i = i + 1 { ... }` |
| break / continue | 迴圈中斷與繼續 |
| read 輸入 | `read x;` 從 stdin 讀取整數 |
| else if 鏈 | `if ... else if ... else ...` |
| 區塊註解 | `/* ... */` 支援巢狀行 |
| 字串串接 | `"Hello" + " World"` |

## EBNF 語法 (新增部分)

```
statement     = ... | for_stmt | read_stmt | break_stmt | continue_stmt
for_stmt      = "for" [assignment] ";" [expression] ";" [assignment] block
break_stmt    = "break" ";"
continue_stmt = "continue" ";"
read_stmt     = "read" ident ";"
factor        = ... | array_literal | index_expr
array_literal = "[" [ expression { "," expression } ] "]"
index_expr    = ident "[" expression "]"
```

## 檔案結構

- `sp3i.py` - 直譯器 (tokenizer → parser → AST → 直接執行)
- `sp3c.py` - 編譯器 + 堆疊機 VM (tokenizer → parser → AST → bytecode → VM 執行)
- `sp3a.py` - Bytecode 組譯器 (文字格式 → 二進位格式)
- `sp3d.py` - Bytecode 反組譯器 (二進位格式 → 文字格式)
- `example.sp3` - 範例程式
- `README.md` - 本說明文件

## 執行方式

### 直譯器

```bash
python sp3i.py example.sp3
```

### 編譯器 + VM

```bash
python sp3c.py example.sp3
```

### Bytecode 組譯/反組譯

```bash
python sp3c.py example.sp3 > bc.txt   # 輸出 bytecode (需修改 main)
python sp3a.py input.txt output.bc     # 文字 → 二進位
python sp3d.py output.bc output.txt    # 二進位 → 文字
```

## AI 開發工具

本專案使用 OpenCode (開源 AI CLI) 搭配 BigPickle 模型，以命令列方式進行開發。
