# 第 8 章：組合語言、連結與載入

## 8.1 為什麼要學組合語言

組合語言（Assembly）是機器碼的人類可讀表示法。系統程式設計師需要理解組合語言的幾個原因：

1. **除錯**：閱讀編譯器產生的組合語言有助於除錯
2. **效能優化**：識別編譯器未最佳化的關鍵路徑
3. **底層控制**：某些系統操作（如 context switch）需要組合語言
4. **安全分析**：理解緩衝區溢位等漏洞

## 8.2 x86-64 基本語法（AT&T 風格）

```asm
# 基本指令格式: opcode source, dest

# 資料傳送
mov %rax, %rbx    # rax → rbx
mov $42, %rax     # 立即值 42 → rax
mov (%rbx), %rax  # 從 rbx 指向的記憶體讀取→ rax

# 算術運算
add %rcx, %rax    # rax = rax + rcx
sub $1, %rax      # rax = rax - 1
imul %rbx, %rax   # rax = rax * rbx

# 比較與跳躍
cmp $0, %rax      # 比較 rax 與 0
je label          # 相等則跳躍
jne label         # 不相等則跳躍
jg label          # 大於則跳躍
jl label          # 小於則跳躍

# 堆疊操作
push %rbp         # 將 rbp 壓入堆疊
pop %rbp          # 從堆疊彈出到 rbp
call function     # 呼叫函數
ret               # 從函數返回
```

## 8.3 C 嵌入組合語言

```c
#include <stdio.h>

int main() {
    int a = 10, b = 20, result;
    
    // 嵌入組合語言進行加法
    asm volatile (
        "mov %1, %%eax\n"
        "add %2, %%eax\n"
        "mov %%eax, %0\n"
        : "=r" (result)     // 輸出運算元
        : "r" (a), "r" (b)  // 輸入運算元
        : "%eax"            // 被修改的暫存器
    );
    
    printf("%d + %d = %d\n", a, b, result);
    return 0;
}
```

## 8.4 函數呼叫約定（Calling Convention）

x86-64 Linux 使用 System V AMD64 ABI：

| 參數位置 | 暫存器 |
|---------|--------|
| 1st | RDI |
| 2nd | RSI |
| 3rd | RDX |
| 4th | RCX |
| 5th | R8 |
| 6th | R9 |
| 7+ | 堆疊 |

```c
// C 函數
long add_four(long a, long b, long c, long d) {
    return a + b + c + d;
}
```

對應的組合語言：

```asm
add_four:
    add %rsi, %rdi    # a += b
    add %rdx, %rdi    # a += c
    add %rcx, %rdi    # a += d
    mov %rdi, %rax    # 回傳值放 rax
    ret
```

## 8.5 編譯流程

```
原始碼 (.c) → [預處理器] → 展開的原始碼 (.i)
            → [編譯器]   → 組合語言 (.s)
            → [組譯器]   → 目的檔 (.o)
            → [連結器]   → 可執行檔
```

```bash
# 逐步編譯
gcc -E program.c -o program.i    # 預處理
gcc -S program.i -o program.s    # 編譯成組合語言
gcc -c program.s -o program.o    # 組譯成目的檔
gcc program.o -o program         # 連結成可執行檔

# 或一步完成
gcc program.c -o program
```

## 8.6 目的檔格式（ELF）

Linux 使用 ELF（Executable and Linkable Format）格式：

```bash
# 檢視 ELF 檔案資訊
file program
readelf -h program     # ELF 標頭
readelf -S program     # 區段表
readelf -s program     # 符號表
objdump -d program     # 反組譯
```

### ELF 檔案結構

```
ELF 標頭
├── 程式標頭表（執行用）
└── 區段標頭表（連結用）
    ├── .text    — 程式碼
    ├── .data    — 已初始化資料
    ├── .bss     — 未初始化資料
    ├── .rodata  — 唯讀資料
    ├── .symtab  — 符號表
    └── .strtab  — 字串表
```

## 8.7 靜態連結 vs 動態連結

### 靜態連結

```bash
# 靜態連結（函式庫直接嵌入可執行檔）
gcc -static -o program_static program.c
ls -la program_static  # 檔案較大
```

### 動態連結

```bash
# 動態連結（執行時載入共享函式庫）
gcc -o program_dynamic program.c
ls -la program_dynamic # 檔案較小
ldd program_dynamic    # 檢視依賴的共享函式庫
```

```c
// 動態載入共享函式庫
#include <stdio.h>
#include <dlfcn.h>

int main() {
    void *handle = dlopen("libm.so.6", RTLD_LAZY);
    
    if (!handle) {
        fprintf(stderr, "dlopen 失敗: %s\n", dlerror());
        return 1;
    }
    
    double (*sqrt_func)(double) = dlsym(handle, "sqrt");
    
    if (!sqrt_func) {
        fprintf(stderr, "dlsym 失敗: %s\n", dlerror());
        return 1;
    }
    
    printf("sqrt(16) = %f\n", sqrt_func(16.0));
    
    dlclose(handle);
    return 0;
}
```

```bash
gcc -ldl -o dl_demo dl_demo.c
```

## 8.8 載入器（Loader）

載入器負責將可執行檔載入記憶體並執行：

```c
#include <stdio.h>
#include <unistd.h>
#include <sys/types.h>

// 模擬載入器的基本流程
int main() {
    printf("=== 載入器模擬 ===\n");
    
    // 1. 讀取 ELF 標頭
    printf("1. 讀取 ELF 標頭\n");
    
    // 2. 建立虛擬位址空間
    printf("2. 建立虛擬位址空間\n");
    
    // 3. 載入區段到記憶體
    printf("3. 載入 .text / .data / .rodata 區段\n");
    
    // 4. 處理動態連結
    printf("4. 解析動態連結符號\n");
    
    // 5. 初始化 BSS
    printf("5. 初始化 BSS 區段（歸零）\n");
    
    // 6. 設定堆疊與 argc/argv
    printf("6. 設定堆疊與命令列參數\n");
    
    // 7. 跳轉到 _start
    printf("7. 跳轉到入口點\n");
    
    return 0;
}
```

## 8.9 分析目的檔範例

```c
// math.c — 簡單的數學函式庫
int global_var = 42;
static int static_var = 0;

int add(int a, int b) {
    return a + b;
}

int multiply(int a, int b) {
    return a * b;
}
```

```bash
# 編譯並分析
gcc -c math.c -o math.o

# 檢視符號表
nm math.o
# 輸出:
# 0000000000000000 T add
# 0000000000000000 D global_var
# 000000000000002e T multiply
# 0000000000000004 b static_var

# 反組譯
objdump -d math.o
```

## 小結

- 組合語言提供底層控制與效能優化能力
- ELF 是 Linux 的標準目的檔格式
- 靜態連結產生較大可執行檔但無執行期依賴
- 動態連結節省空間但需處理相依性
- 載入器負責將程式載入記憶體
