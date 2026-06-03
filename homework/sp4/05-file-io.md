# 第 5 章：檔案系統與輸出入

## 5.1 檔案描述子

在 Linux 中，所有 I/O 操作透過檔案描述子（File Descriptor）進行。檔案描述子是一個非負整數，核心用它來追蹤開啟的檔案。

```
stdin  (0) ← 鍵盤
stdout (1) → 螢幕
stderr (2) → 螢幕
```

## 5.2 open() / close()

```c
#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdlib.h>

int main() {
    int fd = open("test.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644);
    
    if (fd < 0) {
        perror("開啟檔案失敗");
        exit(1);
    }
    
    printf("檔案描述子: %d\n", fd);
    close(fd);
    
    return 0;
}
```

### open() 旗標

| 旗標 | 說明 |
|------|------|
| `O_RDONLY` | 唯讀 |
| `O_WRONLY` | 唯寫 |
| `O_RDWR` | 讀寫 |
| `O_CREAT` | 檔案不存在則建立 |
| `O_TRUNC` | 清空檔案 |
| `O_APPEND` | 附加模式 |

## 5.3 read() / write()

```c
#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>

int main() {
    const char *msg = "Hello, System Programming!\n";
    
    // 寫入檔案
    int fd = open("output.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd < 0) {
        perror("開啟失敗");
        return 1;
    }
    
    ssize_t written = write(fd, msg, strlen(msg));
    printf("寫入 %zd bytes\n", written);
    close(fd);
    
    // 讀取檔案
    fd = open("output.txt", O_RDONLY);
    char buf[256] = {0};
    
    ssize_t bytes = read(fd, buf, sizeof(buf) - 1);
    printf("讀取 %zd bytes: %s", bytes, buf);
    close(fd);
    
    return 0;
}
```

## 5.4 dup() / dup2()

`dup2()` 可以複製檔案描述子，常用於重新導向：

```c
#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdlib.h>

int main() {
    int fd = open("redirect.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644);
    
    if (fd < 0) {
        perror("開啟失敗");
        return 1;
    }
    
    // 將 stdout (1) 重新導向到檔案
    dup2(fd, STDOUT_FILENO);
    close(fd);
    
    // 這些 printf 會寫入檔案而不是螢幕
    printf("這行會寫入 redirect.txt\n");
    printf("標準輸出被重新導向了\n");
    
    return 0;
}
```

### Shell 重新導向的實作

```c
#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/wait.h>

int main() {
    pid_t pid = fork();
    
    if (pid == 0) {
        // 子行程：將 ls 的輸出導向檔案
        int fd = open("ls_output.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644);
        dup2(fd, STDOUT_FILENO);
        close(fd);
        
        execlp("ls", "ls", "-la", NULL);
        perror("exec 失敗");
        return 1;
    }
    
    wait(NULL);
    printf("完成！請查看 ls_output.txt\n");
    
    return 0;
}
```

## 5.5 管線（Pipe）

```c
#include <stdio.h>
#include <unistd.h>
#include <sys/wait.h>
#include <string.h>
#include <stdlib.h>

int main() {
    int pipefd[2];
    
    if (pipe(pipefd) < 0) {
        perror("pipe 失敗");
        return 1;
    }
    
    pid_t pid = fork();
    
    if (pid == 0) {
        // 子行程：寫入管線
        close(pipefd[0]);
        const char *msg = "Hello from child!";
        write(pipefd[1], msg, strlen(msg));
        close(pipefd[1]);
        exit(0);
    }
    
    // 父行程：讀取管線
    close(pipefd[1]);
    char buf[256] = {0};
    read(pipefd[0], buf, sizeof(buf));
    printf("父行程收到: %s\n", buf);
    close(pipefd[0]);
    
    wait(NULL);
    return 0;
}
```

## 5.6 Shell 管線實作（模擬 `ls | wc -l`）

```c
#include <stdio.h>
#include <unistd.h>
#include <sys/wait.h>
#include <stdlib.h>

int main() {
    int pipefd[2];
    pipe(pipefd);
    
    pid_t pid1 = fork();
    
    if (pid1 == 0) {
        // 第一個子行程：ls
        close(pipefd[0]);
        dup2(pipefd[1], STDOUT_FILENO);
        close(pipefd[1]);
        execlp("ls", "ls", NULL);
        perror("exec ls 失敗");
        exit(1);
    }
    
    pid_t pid2 = fork();
    
    if (pid2 == 0) {
        // 第二個子行程：wc -l
        close(pipefd[1]);
        dup2(pipefd[0], STDIN_FILENO);
        close(pipefd[0]);
        execlp("wc", "wc", "-l", NULL);
        perror("exec wc 失敗");
        exit(1);
    }
    
    close(pipefd[0]);
    close(pipefd[1]);
    
    waitpid(pid1, NULL, 0);
    waitpid(pid2, NULL, 0);
    
    return 0;
}
```

## 5.7 lseek() — 檔案定位

```c
#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>

int main() {
    int fd = open("seek.txt", O_RDWR | O_CREAT | O_TRUNC, 0644);
    
    write(fd, "ABCDEFGHIJ", 10);
    
    // 移動到開頭
    lseek(fd, 0, SEEK_SET);
    
    // 移動到第 5 個 byte 並寫入
    lseek(fd, 5, SEEK_SET);
    write(fd, "12345", 5);
    
    close(fd);
    // 結果: "ABCDE12345"
    
    return 0;
}
```

## 5.8 stat() — 取得檔案資訊

```c
#include <stdio.h>
#include <sys/stat.h>
#include <unistd.h>

int main() {
    struct stat st;
    
    if (stat("test.txt", &st) < 0) {
        perror("stat 失敗");
        return 1;
    }
    
    printf("檔案大小: %ld bytes\n", st.st_size);
    printf("權限: %o\n", st.st_mode & 0777);
    printf("硬連結數: %ld\n", st.st_nlink);
    printf("擁有者 UID: %d\n", st.st_uid);
    printf("群組 GID: %d\n", st.st_gid);
    
    return 0;
}
```

## 小結

- 檔案描述子為 I/O 操作的基礎抽象
- `dup2()` 實現重新導向
- `pipe()` 實現行程間資料傳遞
- 管線與重新導向組合可實作 shell 功能
