# mini-chat — 多人聊天室

系統程式期中作業 — 使用 C 語言 + POSIX socket 實作多人即時聊天室。

## 功能

- 多用戶同時連線 (select I/O 多工)
- 自動分配用戶名稱 (user0, user1, ...)
- 修改名稱 `/name <新名稱>`
- 廣播訊息：所有用戶收到
- 私訊 `/msg <用戶> <訊息>`
- 列出線上用戶 `/list`
- 離開 `/quit`

## 編譯

```bash
make
```

## 使用

**啟動伺服器：**
```bash
./server [埠號]   # 預設 9000
```

**啟動客戶端：**
```bash
./client [主機] [埠號]   # 預設 127.0.0.1:9000
```

## 架構

```
server.c ← select() 管理所有 client fd，處理命令與轉發訊息
client.c ← 雙向 select()：同時監控 stdin 與 socket
```

## AI 使用聲明

本作業使用 GitHub Copilot (opencode) 輔助撰寫，模型為 opencode/big-pickle。
所有程式碼經本人理解與測試後繳交，無直接複製同學或網路專案。
