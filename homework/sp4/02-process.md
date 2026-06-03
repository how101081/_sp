# 第 2 章：行程管理

## 2.1 行程的概念

行程（Process）是執行中的程式實例。每個行程擁有獨立的：
- **位址空間**：程式碼、資料、堆疊、堆積
- **系統資源**：檔案描述子、訊號處理器
- **執行狀態**：暫存器值、程式計數器

## 2.2 行程狀態

```
建立 → 就緒 ↔ 執行 → 終止
          ↓
        阻塞
```

| 狀態 | 說明 |
|------|------|
| 執行（Running） | 正在 CPU 上執行 |
| 就緒（Ready） | 等待 CPU 排程 |
| 阻塞（Blocked） | 等待 I/O 或事件 |
| 殭屍（Zombie） | 已終止但父行程未回收 |
| 孤兒（Orphan） | 父行程先終止 |

## 2.3 fork() — 建立行程

```c
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>

int main() {
    pid_t pid = fork();
    
    if (pid < 0) {
        perror("fork 失敗");
        exit(1);
    }
    
    if (pid == 0) {
        // 子行程
        printf("[子] PID: %d, 父 PID: %d\n", getpid(), getppid());
    } else {
        // 父行程
        printf("[父] PID: %d, 子 PID: %d\n", getpid(), pid);
    }
    
    return 0;
}
```

### fork() 的行為

- 父行程回傳子行程的 PID
- 子行程回傳 0
- 子行程複製父行程的位址空間（寫時複製，Copy-on-Write）

## 2.4 exec() — 執行程式

```c
#include <stdio.h>
#include <unistd.h>
#include <sys/wait.h>

int main() {
    pid_t pid = fork();
    
    if (pid == 0) {
        // 子行程執行 ls 命令
        execlp("ls", "ls", "-la", NULL);
        perror("exec 失敗");
        return 1;
    }
    
    // 父行程等待子行程結束
    int status;
    waitpid(pid, &status, 0);
    printf("子行程結束，狀態: %d\n", WEXITSTATUS(status));
    
    return 0;
}
```

### exec 家族

| 函數 | 說明 |
|------|------|
| `execlp()` | 透過 PATH 搜尋，參數串列 |
| `execvp()` | 透過 PATH 搜尋，參數陣列 |
| `execle()` | 指定路徑，可傳環境變數 |
| `execvpe()` | 指定路徑 + 環境變數 |

## 2.5 wait() 與 waitpid()

```c
#include <stdio.h>
#include <unistd.h>
#include <sys/wait.h>

int main() {
    pid_t pid = fork();
    
    if (pid == 0) {
        printf("子行程工作中...\n");
        sleep(2);
        printf("子行程結束\n");
        return 42;
    }
    
    int status;
    wait(&status);
    
    if (WIFEXITED(status)) {
        printf("子行程正常結束，回傳值: %d\n", WEXITSTATUS(status));
    }
    
    return 0;
}
```

## 2.6 殭屍行程與孤兒行程

```c
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>

int main() {
    pid_t pid = fork();
    
    if (pid == 0) {
        printf("子行程結束\n");
        exit(0);
    }
    
    // 父行程不呼叫 wait()
    sleep(30);
    printf("父行程結束\n");
    
    return 0;
}
```

> **注意**：父行程應呼叫 `wait()` 回收子行程，否則會產生殭屍行程。

## 2.7 訊號處理

```c
#include <stdio.h>
#include <signal.h>
#include <unistd.h>

void handler(int sig) {
    printf("收到訊號: %d\n", sig);
}

int main() {
    signal(SIGINT, handler);
    
    printf("按 Ctrl+C 測試訊號處理\n");
    
    while (1) {
        sleep(1);
    }
    
    return 0;
}
```

| 訊號 | 預設行為 | 用途 |
|------|---------|------|
| SIGINT (2) | 終止行程 | Ctrl+C |
| SIGKILL (9) | 終止行程 | 強制終止（不可忽略） |
| SIGSEGV (11) | 終止 + 核心轉儲 | 記憶體存取錯誤 |
| SIGTERM (15) | 終止行程 | 優雅終止 |

## 小結

- `fork()` 建立新行程，回傳值區分父子
- `exec()` 家族替換行程映像
- `wait()` / `waitpid()` 回收子行程資源
- 訊號提供非同步事件處理機制
