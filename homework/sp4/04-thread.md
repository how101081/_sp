# 第 4 章：執行緒與並行程式設計

## 4.1 執行緒簡介

執行緒（Thread）是 CPU 排程的最小單位。同一行程內的多個執行緒共享記憶體，但各有獨立的堆疊。

```
行程
├── 位址空間（程式碼、資料、堆積）
├── 執行緒 1（堆疊、暫存器）
├── 執行緒 2（堆疊、暫存器）
└── 執行緒 3（堆疊、暫存器）
```

## 4.2 pthread 基本使用

```c
#include <stdio.h>
#include <pthread.h>
#include <unistd.h>

void *thread_func(void *arg) {
    int id = *(int *)arg;
    printf("執行緒 %d 啟動，PID: %d\n", id, getpid());
    sleep(1);
    printf("執行緒 %d 結束\n", id);
    return NULL;
}

int main() {
    pthread_t t1, t2;
    int id1 = 1, id2 = 2;
    
    pthread_create(&t1, NULL, thread_func, &id1);
    pthread_create(&t2, NULL, thread_func, &id2);
    
    pthread_join(t1, NULL);
    pthread_join(t2, NULL);
    
    printf("主執行緒結束\n");
    return 0;
}
```

編譯時需連結 pthread 函式庫：

```bash
gcc -pthread -o thread thread.c
```

## 4.3 Race Condition（競爭條件）

```c
#include <stdio.h>
#include <pthread.h>

int counter = 0;

void *increment(void *arg) {
    for (int i = 0; i < 1000000; i++) {
        counter++;  // 非原子操作！
    }
    return NULL;
}

int main() {
    pthread_t t1, t2;
    
    pthread_create(&t1, NULL, increment, NULL);
    pthread_create(&t2, NULL, increment, NULL);
    
    pthread_join(t1, NULL);
    pthread_join(t2, NULL);
    
    printf("預期結果: 2000000, 實際結果: %d\n", counter);
    return 0;
}
```

> `counter++` 並非原子操作，它包含讀取、修改、寫入三個步驟。

## 4.4 Mutex（互斥鎖）

```c
#include <stdio.h>
#include <pthread.h>

int counter = 0;
pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;

void *increment(void *arg) {
    for (int i = 0; i < 1000000; i++) {
        pthread_mutex_lock(&mutex);
        counter++;
        pthread_mutex_unlock(&mutex);
    }
    return NULL;
}

int main() {
    pthread_t t1, t2;
    
    pthread_create(&t1, NULL, increment, NULL);
    pthread_create(&t2, NULL, increment, NULL);
    
    pthread_join(t1, NULL);
    pthread_join(t2, NULL);
    
    printf("預期結果: 2000000, 實際結果: %d\n", counter);
    
    pthread_mutex_destroy(&mutex);
    return 0;
}
```

## 4.5 Deadlock（死結）

```c
#include <stdio.h>
#include <pthread.h>
#include <unistd.h>

pthread_mutex_t lock1 = PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_t lock2 = PTHREAD_MUTEX_INITIALIZER;

void *thread_a(void *arg) {
    pthread_mutex_lock(&lock1);
    printf("執行緒 A 取得 lock1\n");
    sleep(1);
    
    pthread_mutex_lock(&lock2);
    printf("執行緒 A 取得 lock2\n");
    
    pthread_mutex_unlock(&lock2);
    pthread_mutex_unlock(&lock1);
    return NULL;
}

void *thread_b(void *arg) {
    pthread_mutex_lock(&lock2);
    printf("執行緒 B 取得 lock2\n");
    sleep(1);
    
    pthread_mutex_lock(&lock1);
    printf("執行緒 B 取得 lock1\n");
    
    pthread_mutex_unlock(&lock1);
    pthread_mutex_unlock(&lock2);
    return NULL;
}

int main() {
    pthread_t t1, t2;
    
    pthread_create(&t1, NULL, thread_a, NULL);
    pthread_create(&t2, NULL, thread_b, NULL);
    
    pthread_join(t1, NULL);
    pthread_join(t2, NULL);
    
    return 0;
}
```

### 避免死結的原則

1. **固定鎖順序**：所有執行緒以相同順序取得鎖
2. **嘗試鎖定**：使用 `pthread_mutex_trylock()`
3. **縮小鎖範圍**：只保護必要的程式碼

## 4.6 條件變數

```c
#include <stdio.h>
#include <pthread.h>

pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;
pthread_cond_t cond = PTHREAD_COND_INITIALIZER;
int ready = 0;

void *worker(void *arg) {
    pthread_mutex_lock(&mutex);
    while (!ready) {
        pthread_cond_wait(&cond, &mutex);
    }
    printf("工作者：收到通知，開始工作\n");
    pthread_mutex_unlock(&mutex);
    return NULL;
}

void *notifier(void *arg) {
    sleep(1);
    pthread_mutex_lock(&mutex);
    ready = 1;
    printf("通知者：發送通知\n");
    pthread_cond_signal(&cond);
    pthread_mutex_unlock(&mutex);
    return NULL;
}

int main() {
    pthread_t t1, t2;
    
    pthread_create(&t1, NULL, worker, NULL);
    pthread_create(&t2, NULL, notifier, NULL);
    
    pthread_join(t1, NULL);
    pthread_join(t2, NULL);
    
    return 0;
}
```

## 4.7 執行緒安全佇列範例

```c
#include <stdio.h>
#include <pthread.h>
#include <stdlib.h>

typedef struct {
    int *buf;
    int size;
    int head, tail;
    pthread_mutex_t mutex;
    pthread_cond_t not_full;
    pthread_cond_t not_empty;
} queue_t;

queue_t *queue_create(int size) {
    queue_t *q = malloc(sizeof(queue_t));
    q->buf = malloc(size * sizeof(int));
    q->size = size;
    q->head = q->tail = 0;
    pthread_mutex_init(&q->mutex, NULL);
    pthread_cond_init(&q->not_full, NULL);
    pthread_cond_init(&q->not_empty, NULL);
    return q;
}

void queue_push(queue_t *q, int val) {
    pthread_mutex_lock(&q->mutex);
    while ((q->tail + 1) % q->size == q->head) {
        pthread_cond_wait(&q->not_full, &q->mutex);
    }
    q->buf[q->tail] = val;
    q->tail = (q->tail + 1) % q->size;
    pthread_cond_signal(&q->not_empty);
    pthread_mutex_unlock(&q->mutex);
}

int queue_pop(queue_t *q) {
    pthread_mutex_lock(&q->mutex);
    while (q->head == q->tail) {
        pthread_cond_wait(&q->not_empty, &q->mutex);
    }
    int val = q->buf[q->head];
    q->head = (q->head + 1) % q->size;
    pthread_cond_signal(&q->not_full);
    pthread_mutex_unlock(&q->mutex);
    return val;
}
```

## 小結

- 執行緒共享記憶體但各有獨立堆疊
- Mutex 保護共用資源避免 Race Condition
- 不當的鎖順序會導致 Deadlock
- 條件變數實現執行緒間的通知機制
