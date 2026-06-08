# 系統程式 — 平時作業總匯

## AI 使用聲明

本作業全程使用 AI 輔助撰寫（GitHub Copilot / opencode），模型為 opencode/big-pickle。
所有程式碼經本人理解、測試與修改後繳交，無直接複製同學或網路專案。
部分程式碼參考課程教材 [ccckmit/course0](https://github.com/ccckmit/course0/tree/main/code) 中的範例。

---

## 作業總覽

| 作業 | 主題 | 語言 | 說明 |
|------|------|------|------|
| sp1 | p0 編譯器 — while 與函數呼叫 | C | 擴充 p0 語言支援 while 迴圈和遞迴函數 |
| sp2 | SL 語言 — 直譯器 + 編譯器 | Python | 自訂語言 SL 的 AST 直譯器與 bytecode VM |
| sp3 | Mini-Rsync — 快照備份工具 | Python | SHA256 增量備份、檔案同步與差異比對 |
| sp4 | AI 教你系統程式 — 教科書 | Markdown | 八章系統程式主題教材 |
| sp5 | Thread 同步 — 經典並行問題 | C (pthreads) | 銀行 race condition、生產者消費者、哲學家 |
| sp6 | Unix 行程與檔案操作 | C | fd、fork、exec、dup2、mini shell |
| sp期中 | Mini-Chat — 多人聊天室 | C (sockets) | select I/O 多工 TCP 聊天伺服器 |

---

## sp1 — p0 編譯器：while 與函數呼叫

**目錄：** [`../sp1/08-comment/`](../sp1/08-comment/)

以 C 語言實作 p0 小型語言的編譯器 + 堆疊機 VM，擴充語法支援：

- **`while` 迴圈** — 使用 backpatching 技術處理條件跳轉（`JMP_F`）與迴圈回跳（`JMP`）
- **函數定義與遞迴** — 透過 stack frame 管理（`PARAM` / `CALL` / `RET_VAL`）支援遞迴呼叫
- **if 條件判斷** — 條件跳轉選擇分支
- **四元式中間碼** — 編譯為 triple/quadruple 形式，再交由 VM 執行

**關鍵檔案：** `HW_sp1.c`（編譯器 + VM）、`test.txt`（測試程式）

---

## sp2 — SL 語言：直譯器與編譯器

**目錄：** [`../sp2/`](../sp2/)

為自訂語言 **SL (Simple Language)** 實作雙重執行途徑：

- **`sp2i.py`** — 直譯器：tokenizer → parser → AST → 直接執行
- **`sp2c.py`** — 編譯器 + VM：tokenizer → parser → AST → bytecode → 堆疊機執行

支援整數運算、比較、邏輯運算、if/else、while、函數定義與遞迴、print、註解。
完整 EBNF 語法定義於 README。

---

## sp3 — Mini-Rsync：快照備份工具

**目錄：** [`../sp3/`](../sp3/)

Python 實作的 rsync 風格備份工具，五個子命令：

| 命令 | 功能 |
|------|------|
| `snapshot` | 掃描目錄，SHA256 hash + metadata → JSON |
| `sync` | 增量同步（僅複製 hash 不同之檔案） |
| `restore` | 比對目錄與快照，列出不一致檔案 |
| `diff` | 比對兩個快照，列出新增/刪除/修改 |
| `hash` | 計算目錄中所有檔案的 SHA256 |

**關鍵檔案：** `rsync.py`（約 205 行）

---

## sp4 — AI 教你系統程式（教科書）

**目錄：** [`../sp4/`](../sp4/)

八章系統程式教材，C 程式碼範例：

| 章節 | 主題 |
|------|------|
| 01 | 系統程式導論 |
| 02 | 行程管理 |
| 03 | 記憶體管理（虛擬記憶體、分頁、MMU） |
| 04 | 執行緒與並行程式設計 |
| 05 | 檔案系統與 I/O |
| 06 | 行程間通訊 (IPC) |
| 07 | 網路程式設計 (socket API) |
| 08 | 組合語言、連結與載入 |

---

## sp5 — Thread 同步：經典並行問題

**目錄：** [`../sp5/`](../sp5/)

C + pthreads 實作三個經典同步問題：

| 程式 | 機制 | 說明 |
|------|------|------|
| `bank.c` | Mutex | 8 執行緒存提款，避免 race condition |
| `producer_consumer.c` | Semaphore + Mutex | 環形緩衝區，empty/full 信號量 |
| `dining_philosophers.c` | Mutex（交替順序） | 5 位哲學家，奇偶不同取叉順序避開 deadlock |

---

## sp6 — Unix 行程與檔案操作

**目錄：** [`../sp6/`](../sp6/)

循序漸進的五個 C 程式：

| 檔案 | 系統呼叫 | 概念 |
|------|---------|------|
| `demo_fd.c` | open/close/read/write | 檔案描述子與 FD 分配規則 |
| `demo_fork.c` | fork/waitpid | 行程建立與回收 |
| `demo_exec.c` | fork + execvp | 執行程式 |
| `demo_redirect.c` | dup2 | I/O 重導向（`>`、`<`） |
| `mini_shell.c` | fork + execvp + dup2 | 簡易 shell（`<`、`>`、`&`、`exit`） |

---

## sp期中 — Mini-Chat：多人聊天室

**目錄：** [`../sp期中/mini-chat/`](../sp期中/mini-chat/)

C + POSIX socket 實作的 TCP 多人聊天室：

- **`server.c`** — select() I/O 多工，最多 32 用戶同時連線
- **`client.c`** — select() 同時監控鍵盤輸入與伺服器訊息

支援指令：`/name`（改名）、`/msg`（私訊）、`/list`（用戶列表）、`/quit`（離開）

---

> 所有原始碼與完整說明請點擊各作業目錄連結。
