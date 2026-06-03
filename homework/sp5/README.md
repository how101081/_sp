# Thread 程式說明文件

## Thread（執行緒）簡介

執行緒（Thread）是 CPU 排程的最小單位。同一行程內的多個執行緒共享位址空間（程式碼、資料、堆積），但各有獨立的堆疊與暫存器。

```c
#include <stdio.h>
#include <pthread.h>
#include <unistd.h>

void *print_msg(void *arg) {
    char *msg = (char *)arg;
    for (int i = 0; i < 3; i++) {
        printf("%s: %d\n", msg, i);
        sleep(1);
    }
    return NULL;
}

int main() {
    pthread_t t1, t2;
    pthread_create(&t1, NULL, print_msg, "Thread A");
    pthread_create(&t2, NULL, print_msg, "Thread B");
    pthread_join(t1, NULL);
    pthread_join(t2, NULL);
    return 0;
}
```

```bash
gcc -pthread -o thread thread.c && ./thread
```

## Race Condition（競爭條件）

當多個執行緒同時讀寫共享資料，且執行順序影響結果時，就產生了 Race Condition。

```c
#include <stdio.h>
#include <pthread.h>

int counter = 0;

void *inc(void *arg) {
    for (int i = 0; i < 1000000; i++)
        counter++;  // 非原子操作！
    return NULL;
}

int main() {
    pthread_t t1, t2;
    pthread_create(&t1, NULL, inc, NULL);
    pthread_create(&t2, NULL, inc, NULL);
    pthread_join(t1, NULL);
    pthread_join(t2, NULL);
    printf("Expected: 2000000, Actual: %d\n", counter);
    return 0;
}
```

`counter++` 在機器碼層級包含三個步驟：LOAD → ADD → STORE。若兩個執行緒交錯執行，就會導致結果不正確。

## Mutex（互斥鎖）

Mutex 確保同一時間只有一個執行緒能進入臨界區段（Critical Section）。

```c
pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;

void *safe_inc(void *arg) {
    for (int i = 0; i < 1000000; i++) {
        pthread_mutex_lock(&mutex);
        counter++;
        pthread_mutex_unlock(&mutex);
    }
    return NULL;
}
```

## Deadlock（死結）

當兩個以上的執行緒彼此等待對方持有的鎖，導致所有執行緒都無法繼續執行，即為 Deadlock。

### 死結四要件

1. **互斥（Mutual Exclusion）**：資源一次只能被一個執行緒使用
2. **持有並等待（Hold and Wait）**：執行緒持有資源的同時等待其他資源
3. **不可搶佔（No Preemption）**：資源不能被強制釋放
4. **循環等待（Circular Wait）**：形成等待環

### 避免 Deadlock 的方法

- 固定鎖順序：所有執行緒以相同順序取得鎖
- 交替順序：奇偶數採用不同順序，破壞循環等待

---

## 程式一：銀行存提款模擬（bank.c）

### 問題描述
模擬銀行帳戶的存款和提款操作。使用 8 個執行緒（4 存 4 提），總計 100,000 次操作，最終餘額應與初始餘額相同。

### 解決方案
使用 Mutex 保護餘額的讀寫操作，確保每次存/提款為原子操作。

### 執行結果
```
=== Bank Account Simulation ===
Initial balance: 1000000
Threads: 8, Operations per thread: 12500
Total operations: 100000
Final balance: 1000000
Result: CORRECT
```

---

## 程式二：生產者消費者問題（producer_consumer.c）

### 問題描述
生產者將資料放入大小為 5 的環形緩衝區，消費者從緩衝區取出資料，總共生產消費 20 個項目。

### 解決方案
使用 Semaphore 搭配 Mutex：
- `empty` 信號量：記錄空槽數量（初始 = 5）
- `full` 信號量：記錄滿槽數量（初始 = 0）
- `mutex`：保護緩衝區的互斥存取

### 執行結果
生產者與消費者正確交替執行，最終緩衝區計數為 0。

---

## 程式三：哲學家用餐問題（dining_philosophers.c）

### 問題描述
5 位哲學家圍坐圓桌，每人左右各有一把叉子。需同時拿起左右叉子才能用餐。

### 問題分析
若所有哲學家都先拿左邊叉子，會形成循環等待 → Deadlock。

### 解決方案
採用交替順序策略：
- 偶數 ID：先拿左邊，再拿右邊
- 奇數 ID：先拿右邊，再拿左邊

破壞循環等待條件，避免 Deadlock。

### 執行結果
```
=== Results ===
Philosopher 0 ate 3 meals
Philosopher 1 ate 3 meals
Philosopher 2 ate 3 meals
Philosopher 3 ate 3 meals
Philosopher 4 ate 3 meals
```

---

## 總結

| 程式 | 同步機制 | 解決問題 |
|------|----------|---------|
| bank.c | Mutex | Race Condition |
| producer_consumer.c | Semaphore + Mutex | 生產者-消費者同步 |
| dining_philosophers.c | Mutex（交替順序） | Deadlock |
