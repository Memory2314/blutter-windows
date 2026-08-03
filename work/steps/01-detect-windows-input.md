# Step 01 — 识别 Windows 输入

## 目标

对 Flutter Windows 安装目录正确识别：

- `data\app.so`（ELF 快照）
- `flutter_windows.dll`（PE 引擎）
- flags → `windows` + `x64` + `no-compressed-pointers`
- Dart 版本（如 `3.3.4`）

**本步不编译 Dart VM，不加载快照。**

## 改动文件

- `extract_dart_info.py` — PE 引擎解析；OS/arch 优先取自 snapshot flags
- `blutter.py` — 支持 Windows 目录布局；新增 `--detect-only`

## 操作

```powershell
cd f:\reverse\blutter
python blutter.py f:\reverse\repable f:\reverse\blutter\work\out_detect --detect-only
```

## 验收（Reqable）

已于本机验证通过：

```text
Dart version: 3.3.4, Snapshot: ee1eb666c76a5cb7746faf39d0b97547, Target: windows x64
flags: product ... x64 windows no-compressed-pointers null-safety
DETECT_ONLY: ok
lib_name: dartvm3.3.4_windows_x64
compressed_ptrs: False
```

- [x] Target 为 `windows x64`
- [x] flags 含 `no-compressed-pointers`
- [x] 不触发 cmake / ninja

## 下一跳

[02-build-dartvm-windows-x64.md](02-build-dartvm-windows-x64.md)
