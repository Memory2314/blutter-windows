# blutter-windows

[English](README.md) | 中文文档

基于 [worawit/blutter](https://github.com/worawit/blutter) 的 fork，增加 **Flutter Windows（x64）** 支持。

Blutter 通过编译匹配版本的 Dart AOT Runtime，加载快照（`libapp.so` / `app.so`）来逆向 Flutter 应用。

| 目标 | 上游 | 本 fork |
|------|------|---------|
| Android `libapp.so`（arm64） | 支持 | 支持（保持兼容） |
| Flutter Windows（`data/app.so` + `flutter_windows.dll`，x64） | 不支持 | **支持（MVP）** |

**Windows MVP 能力：** 探测输入 → 编译 `windows/x64` Dart VM → dump Object Pool → asm 注释 + IDA 改名脚本。

完整 x64 IL（对齐 arm64）尚未移植。移植记录见 [`work/steps/`](work/steps/README.md)。

目前主要适配较新的 Dart 版本。

## 预编译 Release（Windows）

若目标应用是 **Dart 3.3.4**、且常见桌面布局 **`no-compressed-pointers`**：

1. 到 [Releases](https://github.com/1903247335/blutter-windows/releases) 下载最新压缩包
2. 解压到本仓库的 `bin\`（或把该目录加入 `PATH`）
3. 仍需 Python 3 做版本探测与调度：

```powershell
python blutter.py path\to\flutter_app out_dir
```

压缩包一般包含：

| 文件 | 作用 |
|------|------|
| `blutter_dartvm3.3.4_windows_x64_no-compressed-ptrs.exe` | 完整 MVP 分析（asm + IDA） |
| `blutter_dartvm3.3.4_windows_x64_no-compressed-ptrs_no-analysis.exe` | 更快，只 dump 对象池 |
| `capstone.dll` / `icuuc73.dll` / `icudt73.dll` | 运行依赖 |

其他 Dart 版本仍需本机编译（见下文）。

## 环境准备

需要较新的 C++20 工具链（g++≥13、Clang≥16，或最新 MSVC）。

### Windows（从源码编译）

- Git + Python 3
- Visual Studio（勾选「使用 C++ 的桌面开发」和 CMake）
- 依赖库：

```powershell
python scripts\init_env_win.py
```

- 编译前打开 **x64 Native Tools Command Prompt**

### Debian Unstable（gcc 13）

```bash
apt install python3-pyelftools python3-requests git cmake ninja-build \
    build-essential pkg-config libicu-dev libcapstone-dev
```

### macOS

```bash
brew install cmake ninja pkg-config icu4c capstone
pip3 install pyelftools requests
# Ventura/Sonoma 可能需要: brew install llvm@16
```

## 用法

### Flutter Windows

指向安装目录（含 `flutter_windows.dll` 与 `data/app.so`）：

```powershell
python blutter.py path\to\flutter_app out_dir
```

仅探测（不编译、不 dump）：

```powershell
python blutter.py path\to\flutter_app out_dir --detect-only
```

跳过反汇编，只 dump 对象池：

```powershell
python blutter.py path\to\flutter_app out_dir --no-analysis
```

### Android

```bash
python3 blutter.py path/to/app/lib/arm64-v8a out_dir
```

脚本会从引擎识别 Dart 版本；若没有对应 `blutter` 可执行文件，会自动拉取并编译 Dart VM，再分析快照。

## 输出说明

| 路径 | 说明 |
|------|------|
| `pp.txt` | Object Pool（字符串、类型、闭包等） |
| `objs.txt` | 嵌套对象转储 |
| `asm/` | 按库拆分的汇编，带 PP/THR 等注释（x64 为 MVP） |
| `ida_script/` | IDA 批量改名 / 结构注释脚本 |
| `blutter_frida.js` | Frida 脚本模板 |

## 目录结构

| 路径 | 说明 |
|------|------|
| `bin/` | 各版本 `blutter_dartvm<ver>_<os>_<arch>` 可执行文件 |
| `blutter/` | C++ 源码（链接 Dart VM） |
| `build/` | CMake 构建目录（可删） |
| `dartsdk/` | 拉取的 Dart SDK（编完可删） |
| `packages/` | Dart VM 静态库 |
| `scripts/` | 拉取 / 编译辅助脚本 |
| `work/steps/` | Windows 移植分步说明（本 fork） |

## 原理简述（Windows）

1. **认人**：解析 `flutter_windows.dll`（PE）与 `app.so` 快照 flags，得到版本 / os / arch / 是否压缩指针  
2. **对口 VM**：编译 `dartvm*_windows_x64`（桌面常见无压缩指针）  
3. **加载**：Windows 上需 RWX 映射，否则 `Dart_Initialize` 会触发 DEP  
4. **导出**：复用上游 dump / IDA 符号逻辑；另增 x64 反汇编注释（IL 未齐）

更细的踩坑记录见 `work/steps/`。

## 致谢

原项目：[worawit/blutter](https://github.com/worawit/blutter)（MIT）。

## TODO

- x64 完整 IL（对齐 arm64 `asm2il`）
- 更完善的参数 / 返回值恢复
- 更好的 Frida 模板
- 混淆应用
- iOS
- 直接支持 apk / ipa 输入
