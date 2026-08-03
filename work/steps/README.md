# blutter-windows — Windows/x64 移植分步

本仓库：`blutter-windows`（fork of [worawit/blutter](https://github.com/worawit/blutter)）。

目标：分析 Flutter Windows 桌面包（如 `f:\reverse\repable` 的 `data\app.so`）。

## 总进度

| Step | 文件 | 目标 | 状态 |
|------|------|------|------|
| 00 | [00-smoke-android.md](00-smoke-android.md) | 原版安卓链路在本机可编可跑 | 待做 |
| 01 | [01-detect-windows-input.md](01-detect-windows-input.md) | 识别 Win 输入并打印 windows/x64 | **已完成** |
| 02 | [02-build-dartvm-windows-x64.md](02-build-dartvm-windows-x64.md) | 编出 `dartvm*_windows_x64` | **已完成** |
| 03 | [03-load-dump-pp.md](03-load-dump-pp.md) | 加载快照并 dump `pp.txt` | **已完成** |
| 04 | [04-x64-analyzer.md](04-x64-analyzer.md) | x64 反汇编 + asm/IDA | **已完成（MVP）** |

## Reqable 样本已知信息

```text
路径: f:\reverse\repable
app:  data\app.so          (ELF)
engine: flutter_windows.dll (PE)
flags: product ... x64 windows no-compressed-pointers null-safety
snapshot: ee1eb666c76a5cb7746faf39d0b97547
Dart: 3.3.4 (stable)  — 来自 flutter_windows.dll 字符串
```

## 推荐命令（逐步解锁）

```powershell
cd f:\reverse\blutter

# Step 01：只探测，不编译
python blutter.py f:\reverse\repable f:\reverse\blutter\work\out_detect --detect-only

# Step 02+：无分析加载（需 VS x64 Native Tools）
python blutter.py f:\reverse\repable f:\reverse\blutter\work\out_pp --no-analysis
```

## 原则

1. 一步一验收，失败不进入下一步。  
2. 先 `pp.txt`，后 asm。  
3. 安卓原路径保持兼容，不破坏 upstream 行为。
