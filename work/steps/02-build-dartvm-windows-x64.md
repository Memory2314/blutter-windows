# Step 02 — 编译 windows/x64 Dart VM

## 目标

生成与 Reqable 快照匹配的静态库：

```text
packages\lib\dartvm3.3.4_windows_x64.lib
packages\include\dartvm3.3.4\...
```

并编出：

```text
bin\blutter_dartvm3.3.4_windows_x64_no-compressed-ptrs_no-analysis.exe
```

## 前置

- Step 01 验收通过
- x64 Native Tools Command Prompt（`vcvars64.bat`）
- `python scripts\init_env_win.py` 已完成（ICU + Capstone → `bin\`）

## 本步已落地的改动

- `scripts\CMakeLists.txt`：允许 `TARGET_OS=windows` → `DART_TARGET_OS_WINDOWS`
- `dartvm_fetch_build.py`：默认 ZIP 拉 Dart SDK（`BLUTTER_DART_PREFER_ZIP=1`），缓存 `dartsdk\sdk-<ver>.zip`
- `blutter\CMakeLists.txt` + `Disassembler_x64.*`：x64 `--no-analysis` 可链接
- `ElfHelper.cpp`：Windows 下 RWX 映射 `app.so`（避免 DEP 崩在 `Dart_Initialize`）

## 操作

```powershell
cd f:\reverse\blutter
cmd /c "call `"C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars64.bat`" && python -u blutter.py f:\reverse\repable f:\reverse\blutter\work\out_pp --no-analysis --rebuild"
```

若引擎版本探测失败，可手动：

```powershell
python blutter.py f:\reverse\repable\data\app.so f:\reverse\blutter\work\out_pp --no-analysis --dart-version 3.3.4_windows_x64
```

## 验收

- [x] `packages\lib\` 存在 `dartvm3.3.4_windows_x64.lib`（约 19MB）
- [x] `bin\` 存在 `blutter_*windows_x64*no-analysis.exe`
- [x] CMake：`TARGET_OS=windows`、`TARGET_ARCH=x64`、`COMPRESSED_PTRS=0`

## 下一跳

[03-load-dump-pp.md](03-load-dump-pp.md)
