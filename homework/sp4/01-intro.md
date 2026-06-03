# 第 1 章：系統程式導論

## 1.1 什麼是系統程式

系統程式（System Programming）是指直接與作業系統核心互動、管理硬體資源、提供底層服務的程式設計。與應用程式設計不同，系統程式需要深入理解作業系統的內部機制。

### 系統程式的範疇

- **作業系統核心**：行程排程、記憶體管理、檔案系統
- **編譯器與組譯器**：將高階語言轉換為機器碼
- **連結器與載入器**：將目的檔組合成可執行檔
- **驅動程式**：控制硬體設備
- **工具程式**：shell、系統呼叫函式庫

## 1.2 系統程式 vs 應用程式

| 特性 | 系統程式 | 應用程式 |
|------|---------|---------|
| 執行模式 | 核心態 / 使用者態 | 使用者態 |
| 資源存取 | 直接存取硬體 | 透過系統呼叫 |
| 程式語言 | C / Rust / 組合語言 | 任何語言 |
| 錯誤處理 | 需處理底層錯誤 | 可依賴 OS 抽象 |
| 效能要求 | 極高 | 視需求而定 |

## 1.3 系統呼叫（System Call）

系統呼叫是使用者程式與作業系統核心之間的介面。以 Linux 為例：

```c
#include <unistd.h>
#include <stdio.h>

int main() {
    // write 是一個系統呼叫
    write(STDOUT_FILENO, "Hello, System Programming!\n", 28);
    return 0;
}
```

常見的系統呼叫分類：

| 類別 | 系統呼叫範例 |
|------|------------|
| 行程控制 | `fork()`, `exec()`, `exit()` |
| 檔案操作 | `open()`, `read()`, `write()`, `close()` |
| 記憶體管理 | `mmap()`, `brk()`, `sbrk()` |
| 行程間通訊 | `pipe()`, `shmget()`, `msgget()` |
| 網路 | `socket()`, `bind()`, `listen()` |

## 1.4 開發環境

本書使用 Linux 環境（Ubuntu / WSL）搭配 GCC 編譯器：

```bash
# 安裝開發工具
sudo apt install build-essential gdb valgrind

# 編譯與執行
gcc -Wall -o program program.c
./program
```

## 1.5 第一個系統程式

```c
#include <stdio.h>
#include <unistd.h>
#include <sys/types.h>

int main() {
    pid_t pid = getpid();
    pid_t ppid = getppid();
    
    printf("行程 ID: %d\n", pid);
    printf("父行程 ID: %d\n", ppid);
    printf("使用者 ID: %d\n", getuid());
    printf("群組 ID: %d\n", getgid());
    
    return 0;
}
```

## 小結

- 系統程式直接與作業系統核心互動
- 系統呼叫是使用者態與核心態的橋樑
- Linux 提供豐富的系統呼叫 API
