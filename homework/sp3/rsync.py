#!/usr/bin/env python3
"""Mini-Rsync: 自製快照備份與檔案同步工具"""

import os, sys, hashlib, json, time, shutil, argparse
from pathlib import Path

CHUNK_SIZE = 65536

def file_hash(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            buf = f.read(CHUNK_SIZE)
            if not buf:
                break
            h.update(buf)
    return h.hexdigest()

def scan_tree(root):
    root = Path(root).resolve()
    entries = {}
    for p in sorted(root.rglob("*")):
        rel = str(p.relative_to(root))
        if p.is_dir():
            entries[rel] = {"type": "dir"}
        elif p.is_file():
            st = p.stat()
            entries[rel] = {
                "type": "file",
                "size": st.st_size,
                "mtime": st.st_mtime,
                "hash": file_hash(p),
            }
    return entries

def snapshot_cmd(args):
    root = Path(args.dir).resolve()
    if not root.is_dir():
        print(f"Error: {root} is not a directory")
        sys.exit(1)
    entries = scan_tree(root)
    snap = {
        "root": str(root),
        "time": time.time(),
        "entries": entries,
    }
    out = args.output or f"snapshot-{root.name}-{int(time.time())}.json"
    with open(out, "w") as f:
        json.dump(snap, f, indent=2)
    print(f"Snapshot saved: {out} ({len(entries)} entries)")

def load_snapshot(path):
    with open(path) as f:
        return json.load(f)

def sync_cmd(args):
    src = Path(args.src).resolve()
    dst = Path(args.dst).resolve()
    if not src.is_dir():
        print(f"Error: source {src} not found")
        sys.exit(1)
    dst.mkdir(parents=True, exist_ok=True)
    src_entries = scan_tree(src)
    dst_entries = scan_tree(dst) if dst.is_dir() else {}

    copied = 0
    deleted = 0
    skipped = 0

    for rel, info in src_entries.items():
        dst_path = dst / rel
        if info["type"] == "dir":
            dst_path.mkdir(parents=True, exist_ok=True)
            continue
        dst_info = dst_entries.get(rel)
        if dst_info and dst_info["type"] == "file" and dst_info["hash"] == info["hash"]:
            skipped += 1
            continue
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src / rel, dst_path)
        copied += 1
        print(f"  COPY  {rel}")

    if args.delete:
        for rel in list(dst_entries.keys()):
            if rel not in src_entries:
                path = dst / rel
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
                deleted += 1
                print(f"  DEL   {rel}")

    print(f"\nSynced: {copied} copied, {skipped} skipped", end="")
    if args.delete:
        print(f", {deleted} deleted", end="")
    print()

def restore_cmd(args):
    snap = load_snapshot(args.snapshot)
    root = Path(args.dir).resolve()
    root.mkdir(parents=True, exist_ok=True)
    restored = 0
    skipped = 0
    for rel, info in snap["entries"].items():
        path = root / rel
        if info["type"] == "dir":
            path.mkdir(parents=True, exist_ok=True)
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.is_file() and file_hash(path) == info["hash"]:
            skipped += 1
            continue
        print(f"  MISSING or CHANGED: {rel}")
        restored += 1
    if restored == 0:
        print("All files already match snapshot.")
    else:
        print(f"\n{restored} files need restoration. Run sync from snapshot backup.")

def diff_cmd(args):
    s1 = load_snapshot(args.snapshot1)
    s2 = load_snapshot(args.snapshot2)
    e1, e2 = s1["entries"], s2["entries"]
    added = []
    removed = []
    changed = []
    unchanged = 0
    all_keys = set(e1.keys()) | set(e2.keys())
    for k in sorted(all_keys):
        if k not in e1:
            added.append(k)
        elif k not in e2:
            removed.append(k)
        elif e1[k] != e2[k]:
            changed.append(k)
        else:
            unchanged += 1
    print(f"=== Diff: {args.snapshot1} vs {args.snapshot2} ===")
    print(f"Snapshot 1: {s1['root']} @ {time.ctime(s1['time'])}")
    print(f"Snapshot 2: {s2['root']} @ {time.ctime(s2['time'])}")
    print(f"\nUnchanged: {unchanged}")
    if added:
        print(f"\n--- Added ({len(added)}) ---")
        for k in added:
            print(f"  + {k}")
    if removed:
        print(f"\n--- Removed ({len(removed)}) ---")
        for k in removed:
            print(f"  - {k}")
    if changed:
        print(f"\n--- Changed ({len(changed)}) ---")
        for k in changed:
            e1v, e2v = e1[k], e2[k]
            s1_sz = e1v.get("size", "?")
            s2_sz = e2v.get("size", "?")
            print(f"  ~ {k}  ({s1_sz} -> {s2_sz} bytes)")

def hash_cmd(args):
    entries = scan_tree(args.dir)
    for rel, info in sorted(entries.items()):
        if info["type"] == "file":
            print(f"{info['hash']}  {rel}")

def main():
    parser = argparse.ArgumentParser(
        description="Mini-Rsync - 自製快照備份與檔案同步工具",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_snap = sub.add_parser("snapshot", help="建立目錄快照")
    p_snap.add_argument("dir", help="要掃描的目錄")
    p_snap.add_argument("-o", "--output", help="輸出檔案 (預設自動命名)")

    p_sync = sub.add_parser("sync", help="同步原始目錄到目標目錄")
    p_sync.add_argument("src", help="原始目錄")
    p_sync.add_argument("dst", help="目標目錄")
    p_sync.add_argument("--delete", action="store_true", help="刪除目標端多餘的檔案")

    p_res = sub.add_parser("restore", help="比對目錄與快照，列出需還原的檔案")
    p_res.add_argument("snapshot", help="快照 JSON 檔")
    p_res.add_argument("dir", help="要檢查/還原的目錄")

    p_diff = sub.add_parser("diff", help="比對兩個快照的差異")
    p_diff.add_argument("snapshot1", help="第一個快照")
    p_diff.add_argument("snapshot2", help="第二個快照")

    p_hash = sub.add_parser("hash", help="計算目錄中所有檔案的 SHA256")
    p_hash.add_argument("dir", help="目錄路徑")

    args = parser.parse_args()
    if args.cmd == "snapshot":
        snapshot_cmd(args)
    elif args.cmd == "sync":
        sync_cmd(args)
    elif args.cmd == "restore":
        restore_cmd(args)
    elif args.cmd == "diff":
        diff_cmd(args)
    elif args.cmd == "hash":
        hash_cmd(args)

if __name__ == "__main__":
    main()
