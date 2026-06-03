# 第 3 章：記憶體管理

## 3.1 虛擬記憶體

作業系統為每個行程提供獨立的虛擬位址空間，透過 MMU（Memory Management Unit）將虛擬位址映射到實體記憶體。

```
虛擬位址 → [MMU + 分頁表] → 實體位址
```

### 位址空間布局

```
高位址 +------------------+
      | 環境變數/命令列   |
      |------------------|
      | 堆疊（向下成長）  |
      |        ↓         |
      |        ↑         |
      | 堆積（向上成長）  |
      |------------------|
      | BSS (未初始化)    |
      | Data (已初始化)   |
      |------------------|
      | Text (程式碼)     |
低位址 +------------------+
```

## 3.2 動態記憶體配置

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main() {
    // malloc — 配置記憶體
    int *arr = (int *)malloc(5 * sizeof(int));
    if (arr == NULL) {
        fprintf(stderr, "記憶體配置失敗\n");
        return 1;
    }
    
    for (int i = 0; i < 5; i++) {
        arr[i] = i * 10;
    }
    
    // realloc — 調整大小
    int *bigger = (int *)realloc(arr, 10 * sizeof(int));
    if (bigger == NULL) {
        free(arr);
        return 1;
    }
    
    for (int i = 5; i < 10; i++) {
        bigger[i] = i * 10;
    }
    
    // calloc — 配置並歸零
    int *zero = (int *)calloc(5, sizeof(int));
    
    free(bigger);
    free(zero);
    
    return 0;
}
```

## 3.3 sbrk() 與 brk()

`malloc` 底層透過 `sbrk()` / `brk()` 調整行程的堆積邊界：

```c
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>

int main() {
    void *before = sbrk(0);
    printf("堆積目前邊界: %p\n", before);
    
    void *p = malloc(1024 * 1024);
    void *after = sbrk(0);
    printf("配置後邊界: %p\n", after);
    printf("差距: %ld bytes\n", (long)(after - before));
    
    free(p);
    return 0;
}
```

## 3.4 mmap() — 記憶體映射

```c
#include <stdio.h>
#include <sys/mman.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

int main() {
    size_t size = 4096;
    
    // 配置匿名映射（類似 malloc）
    void *addr = mmap(NULL, size,
                      PROT_READ | PROT_WRITE,
                      MAP_PRIVATE | MAP_ANONYMOUS,
                      -1, 0);
    
    if (addr == MAP_FAILED) {
        perror("mmap 失敗");
        return 1;
    }
    
    strcpy((char *)addr, "Hello, mmap!");
    printf("內容: %s\n", (char *)addr);
    
    // 釋放映射
    munmap(addr, size);
    
    return 0;
}
```

### mmap() 參數

| 參數 | 說明 |
|------|------|
| `PROT_READ` | 可讀取 |
| `PROT_WRITE` | 可寫入 |
| `PROT_EXEC` | 可執行 |
| `MAP_PRIVATE` | 私有映射（寫時複製） |
| `MAP_SHARED` | 共享映射 |
| `MAP_ANONYMOUS` | 匿名映射（無後端檔案） |

## 3.5 記憶體對齊與結構體

```c
#include <stdio.h>
#include <stddef.h>

struct packed {
    char a;     // 1 byte
    int  b;     // 4 bytes
    char c;     // 1 byte
};

#pragma pack(push, 1)
struct aligned {
    char a;
    int  b;
    char c;
};
#pragma pack(pop)

int main() {
    printf("packed 大小: %zu bytes\n", sizeof(struct packed));
    printf("aligned 大小: %zu bytes\n", sizeof(struct aligned));
    printf("a offset: %zu\n", offsetof(struct packed, a));
    printf("b offset: %zu\n", offsetof(struct packed, b));
    printf("c offset: %zu\n", offsetof(struct packed, c));
    
    return 0;
}
```

## 3.6 記憶體偵錯（Valgrind）

```bash
# 檢查記憶體洩漏
gcc -g -o program program.c
valgrind --leak-check=full ./program
```

常見的記憶體問題：

```c
#include <stdlib.h>

void memory_leak() {
    int *p = malloc(100);  // 未釋放
}

void use_after_free() {
    int *p = malloc(100);
    free(p);
    p[0] = 42;  // 已釋放記憶體存取
}

void buffer_overflow() {
    int arr[5];
    arr[10] = 42;  // 陣列越界
}

int main() {
    memory_leak();
    return 0;
}
```

## 小結

- 虛擬記憶體提供隔離與安全性
- `malloc` / `free` 管理堆積記憶體
- `mmap()` 提供更底層的記憶體控制
- Valgrind 是必備的記憶體偵錯工具
