# Mini-Rsync - 自製快照備份與檔案同步工具

使用 Python 實作的簡易 rsync 風格工具，支援快照備份、增量同步、差異比對與還原。

## 功能

| 指令 | 說明 |
|------|------|
| `snapshot` | 掃描目錄，記錄所有檔案的 SHA256 hash 與 metadata 至 JSON 快照 |
| `sync` | 同步原始目錄到目標目錄，只複製有變更的檔案（增量同步） |
| `restore` | 比對目錄與快照，列出與快照不一致的檔案 |
| `diff` | 比對兩個快照檔案，顯示新增、刪除、修改的檔案列表 |
| `hash` | 計算目錄中所有檔案的 SHA256 雜湊值 |

## 使用範例

```bash
# 1. 對原始目錄建立快照
python rsync.py snapshot /path/to/source -o backup.snap.json

# 2. 同步到備份目錄（只複製新檔/修改檔）
python rsync.py sync /path/to/source /path/to/backup

# 3. 同步並刪除目標端多餘的檔案
python rsync.py sync /path/to/source /path/to/backup --delete

# 4. 比對兩個快照差異
python rsync.py diff backup1.snap.json backup2.snap.json

# 5. 檢查目錄是否與快照一致（列出不一致檔案）
python rsync.py restore backup.snap.json /path/to/check

# 6. 計算目錄中所有檔案的 hash
python rsync.py hash /path/to/dir
```

## 檔案結構

- `rsync.py` - 主程式（支援 snapshot / sync / restore / diff / hash 子命令）
- `README.md` - 本說明文件

## 實作原理

1. **snapshot**: 遞迴掃描目錄，對每個檔案計算 SHA256 hash，將目錄結構、檔案大小、修改時間、hash 寫入 JSON
2. **sync**: 掃描來源端，對比目標端檔案的 hash，只有 hash 不同的檔案才複製。支援 `--delete` 刪除目標端多餘檔案
3. **restore**: 載入快照 JSON，比對目錄中每個檔案的 hash，標示不一致的檔案
4. **diff**: 載入兩個快照 JSON，比對 entry 字典找出新增/刪除/修改
5. **hash**: 掃描目錄並輸出每個檔案的 SHA256
