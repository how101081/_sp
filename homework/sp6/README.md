# Unix 行程與檔案操作

## 檔案描述子（File Descriptor）

檔案描述子（FD）是非負整數，作業系統用它來識別行程正在存取的資源。

```
行程 FD 表
┌─────┬─────────────┐
│ FD  │ 指向        │
├─────┼─────────────┤
│ 0   │ stdin       │
│ 1   │ stdout      │
│ 2   │ stderr      │
│ 3+  │ 開啟的檔案   │
└─────┴─────────────┘
```

### 三種標準串流

| FD | 常數 | 預設 | 用途 |
|----|------|------|------|
| 0 | `STDIN_FILENO` | 鍵盤 | 標準輸入 |
| 1 | `STDOUT_FILENO` | 螢幕 | 標準輸出 |
| 2 | `STDERR_FILENO` | 螢幕 | 標準錯誤 |

### FD 分配規則

> open() 回傳的 FD = 目前最小的可用非負整數

```c
close(1);                    // 釋放 FD 1
int fd = open("x.txt", ...); // fd = 1（覆蓋 stdout！）
```

---

## open / close / read / write

```c
#include <fcntl.h>
#include <unistd.h>

int fd = open("file.txt", O_RDONLY);
ssize_t n = read(fd, buf, sizeof(buf));
close(fd);

int fd2 = open("out.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644);
write(fd2, "Hello", 5);
close(fd2);
```

| flag | 說明 |
|------|------|
| `O_RDONLY` | 唯讀 |
| `O_WRONLY` | 唯寫 |
| `O_RDWR` | 讀寫 |
| `O_CREAT` | 不存在則建立 |
| `O_TRUNC` | 清空檔案 |
| `O_APPEND` | 附加模式 |

---

## fork — 建立行程

```c
pid_t pid = fork();

if (pid == 0) {
    // 子行程
} else {
    // 父行程，pid 為子行程 ID
}
```

- 父行程回傳子行程 PID，子行程回傳 0
- 子行程複製父行程的位址空間（寫時複製）
- 父子行程共享開啟的檔案描述子

---

## execvp — 執行程式

```c
char *args[] = {"ls", "-la", NULL};
execvp("ls", args);
// 成功不回傳，失敗回傳 -1
```

- execvp 以 PATH 環境變數搜尋執行檔
- 新程式完全取代目前行程映像
- PID 保持不變
- 通常搭配 fork 使用

---

## dup2 — I/O 重導向

```c
int fd = open("out.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644);
dup2(fd, STDOUT_FILENO);  // stdout → 檔案
close(fd);
```

Shell 重新導向的實作原理：

```
ls > out.txt     →  fork + dup2(fd, 1) + exec("ls")
cat < in.txt     →  fork + dup2(fd, 0) + exec("cat")
ls >> out.txt    →  fork + dup2(fd, 1) + exec("ls")  (O_APPEND)
```

---

## 程式說明

### demo_fd.c — 基本檔案操作

展示 open / close / read / write 的基本用法與 FD 分配規則。

```bash
gcc -o demo_fd demo_fd.c && ./demo_fd
```

### demo_fork.c — 行程建立

展示 fork() 建立子行程、父子行程如何透過 fork 回傳值區分、以及 waitpid 回收子行程。

```bash
gcc -o demo_fork demo_fork.c && ./demo_fork
```

### demo_exec.c — 執行程式

展示 fork + execvp 的經典組合，子行程執行 ls 指令，父行程等待。

```bash
gcc -o demo_exec demo_exec.c && ./demo_exec
```

### demo_redirect.c — I/O 重導向

展示 dup2 的三種用法：
1. stdout 重導向到檔案（`> output.txt`）
2. stdin 從檔案讀取（`< output.txt`）
3. fork + exec + dup2 實作 `ls > ls_out.txt`

```bash
gcc -o demo_redirect demo_redirect.c && ./demo_redirect
```

### mini_shell.c — 簡易 Shell

實作一個支援下列功能的簡易 shell：
- 外部指令執行（ls, cat, echo 等）
- 輸入重導向 `<`
- 輸出重導向 `>`
- 背景執行 `&`
- exit 離開

```bash
gcc -o mini_shell mini_shell.c && ./mini_shell

shell> ls
shell> ls > files.txt
shell> cat < files.txt
shell> sleep 10 &
shell> exit
```

---

## 總結

| 系統呼叫 | 功能 | 關鍵概念 |
|---------|------|---------|
| `open()` | 開啟檔案 | 回傳 FD，最小可用原則 |
| `close()` | 關閉檔案 | 釋放 FD |
| `read()` | 讀取資料 | 從 FD 讀入 buf |
| `write()` | 寫入資料 | 從 buf 寫入 FD |
| `fork()` | 建立行程 | 回傳值區分父子，Copy-on-Write |
| `execvp()` | 執行程式 | 取代行程映像，搭配 fork 使用 |
| `dup2()` | 複製 FD | 實現 I/O 重導向 |
