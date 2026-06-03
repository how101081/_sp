# 第 6 章：行程間通訊

## 6.1 IPC 簡介

行程間通訊（Inter-Process Communication, IPC）讓不同行程交換資料。Linux 提供多種 IPC 機制：

| 機制 | 說明 | 適用場景 |
|------|------|---------|
| Pipe | 單向資料流 | 父子行程 |
| FIFO (Named Pipe) | 單向，可跨行程 | 無親屬關係行程 |
| 訊號 (Signal) | 非同步事件通知 | 事件通知 |
| 共享記憶體 | 最高效的資料共享 | 大量資料交換 |
| 訊息佇列 | 訊息導向通訊 | 非同步訊息 |
| Semaphore | 同步機制 | 資源競爭控制 |
| Socket | 跨機器通訊 | 網路通訊 |

## 6.2 匿名管線 (Pipe)

已在第 5 章介紹，此處補充雙向管線範例：

```c
#include <stdio.h>
#include <unistd.h>
#include <sys/wait.h>
#include <string.h>
#include <stdlib.h>

int main() {
    int to_child[2], to_parent[2];
    
    pipe(to_child);
    pipe(to_parent);
    
    pid_t pid = fork();
    
    if (pid == 0) {
        close(to_child[1]);
        close(to_parent[0]);
        
        char msg[256];
        read(to_child[0], msg, sizeof(msg));
        printf("[子] 收到: %s\n", msg);
        
        write(to_parent[1], "OK", 2);
        
        close(to_child[0]);
        close(to_parent[1]);
        exit(0);
    }
    
    close(to_child[0]);
    close(to_parent[1]);
    
    write(to_child[1], "Hello", 5);
    
    char reply[256];
    read(to_parent[0], reply, sizeof(reply));
    printf("[父] 收到回覆: %s\n", reply);
    
    close(to_child[1]);
    close(to_parent[0]);
    wait(NULL);
    
    return 0;
}
```

## 6.3 FIFO (Named Pipe)

FIFO 透過檔案系統中的特殊檔案進行通訊：

```c
// writer.c — 寫入端
#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <string.h>

int main() {
    const char *fifo_path = "/tmp/my_fifo";
    
    // 建立 FIFO
    mkfifo(fifo_path, 0666);
    
    printf("等待讀取端連接...\n");
    int fd = open(fifo_path, O_WRONLY);
    
    const char *msg = "Hello through FIFO!";
    write(fd, msg, strlen(msg));
    close(fd);
    
    unlink(fifo_path);
    return 0;
}
```

```c
// reader.c — 讀取端
#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>

int main() {
    const char *fifo_path = "/tmp/my_fifo";
    
    printf("等待寫入端連接...\n");
    int fd = open(fifo_path, O_RDONLY);
    
    char buf[256] = {0};
    read(fd, buf, sizeof(buf));
    printf("收到: %s\n", buf);
    close(fd);
    
    return 0;
}
```

```bash
# 執行方式（兩個終端機）
gcc -o writer writer.c && gcc -o reader reader.c
./reader &   # 啟動讀取端（背景）
./writer     # 啟動寫入端
```

## 6.4 共享記憶體 (Shared Memory)

```c
#include <stdio.h>
#include <sys/shm.h>
#include <sys/ipc.h>
#include <string.h>
#include <unistd.h>
#include <sys/wait.h>
#include <stdlib.h>

int main() {
    key_t key = IPC_PRIVATE;
    int shmid = shmget(key, 1024, IPC_CREAT | 0666);
    
    if (shmid < 0) {
        perror("shmget 失敗");
        return 1;
    }
    
    pid_t pid = fork();
    
    if (pid == 0) {
        // 子行程：寫入共享記憶體
        void *addr = shmat(shmid, NULL, 0);
        strcpy((char *)addr, "Hello from child!");
        shmdt(addr);
        exit(0);
    }
    
    wait(NULL);
    
    // 父行程：讀取共享記憶體
    void *addr = shmat(shmid, NULL, 0);
    printf("共享記憶體內容: %s\n", (char *)addr);
    shmdt(addr);
    
    // 刪除共享記憶體
    shmctl(shmid, IPC_RMID, NULL);
    
    return 0;
}
```

## 6.5 POSIX 共享記憶體

```c
#include <stdio.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <unistd.h>
#include <string.h>
#include <sys/wait.h>
#include <stdlib.h>

int main() {
    const char *name = "/my_shm";
    size_t size = 4096;
    
    // 建立共享記憶體物件
    int fd = shm_open(name, O_CREAT | O_RDWR, 0666);
    ftruncate(fd, size);
    
    void *addr = mmap(NULL, size, PROT_READ | PROT_WRITE,
                      MAP_SHARED, fd, 0);
    close(fd);
    
    pid_t pid = fork();
    
    if (pid == 0) {
        strcpy((char *)addr, "POSIX shared memory!");
        exit(0);
    }
    
    wait(NULL);
    printf("收到: %s\n", (char *)addr);
    
    munmap(addr, size);
    shm_unlink(name);
    
    return 0;
}
```

```bash
# 編譯時需連結 rt
gcc -lrt -o shm shm.c
```

## 6.6 訊息佇列 (Message Queue)

```c
#include <stdio.h>
#include <sys/msg.h>
#include <sys/ipc.h>
#include <string.h>
#include <unistd.h>
#include <sys/wait.h>
#include <stdlib.h>

struct msg_buf {
    long mtype;
    char mtext[256];
};

int main() {
    key_t key = IPC_PRIVATE;
    int msqid = msgget(key, IPC_CREAT | 0666);
    
    if (msqid < 0) {
        perror("msgget 失敗");
        return 1;
    }
    
    pid_t pid = fork();
    
    if (pid == 0) {
        struct msg_buf msg;
        msgrcv(msqid, &msg, sizeof(msg.mtext), 1, 0);
        printf("[子] 收到: %s\n", msg.mtext);
        exit(0);
    }
    
    struct msg_buf msg = {1, "Hello via msg queue!"};
    msgsnd(msqid, &msg, strlen(msg.mtext) + 1, 0);
    
    wait(NULL);
    msgctl(msqid, IPC_RMID, NULL);
    
    return 0;
}
```

## 6.7 Semaphore（信號量）

```c
#include <stdio.h>
#include <sys/sem.h>
#include <sys/ipc.h>
#include <unistd.h>
#include <sys/wait.h>
#include <stdlib.h>

union semun {
    int val;
    struct semid_ds *buf;
    unsigned short *array;
};

void sem_op(int semid, int op) {
    struct sembuf sb = {0, op, 0};
    semop(semid, &sb, 1);
}

int main() {
    key_t key = IPC_PRIVATE;
    int semid = semget(key, 1, IPC_CREAT | 0666);
    
    union semun su;
    su.val = 1;
    semctl(semid, 0, SETVAL, su);
    
    pid_t pid = fork();
    
    for (int i = 0; i < 5; i++) {
        sem_op(semid, -1);  // P 操作（等待）
        printf("行程 %d 進入臨界區\n", getpid());
        sleep(1);
        printf("行程 %d 離開臨界區\n", getpid());
        sem_op(semid, 1);   // V 操作（釋放）
    }
    
    wait(NULL);
    semctl(semid, 0, IPC_RMID);
    
    return 0;
}
```

## 小結

- Pipe 適用於父子行程的簡單通訊
- FIFO 可跨無親屬關係行程
- 共享記憶體是最快的 IPC 方式
- 訊息佇列提供結構化通訊
- Semaphore 用於同步與互斥
