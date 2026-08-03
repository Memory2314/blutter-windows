# Step 04 — x64 反汇编与 IDA 符号

## 目标

去掉 `--no-analysis`，为 Windows/x64 生成：

- `asm\*`（带 Dart 函数结构与 PP/THR 注释）
- `ida_script\`（给 `app.so.i64` 改名 + Object Pool 结构注释）

## 本步已落地

- `Disassembler_x64.h/.cpp`：Capstone x86_64 + Dart 寄存器别名（PP=R15, THR=R14…）
- `CodeAnalyzer_x64.cpp`：`convertAsm` 重命名寄存器并标注 `PoolOffset` / `ThreadOffset` / `Call`；`asm2il` 暂空（完整 IL 可后续补）
- `DartDumper`：空 IL 安全；`applyStruct4Ida` 支持 x64 MEM 基址
- `blutter.py`：Windows 下经 `vcvars64` 编译；运行前把 `bin\` 放进 PATH（ICU/Capstone DLL）

## 操作

```powershell
cd f:\reverse\blutter
python blutter.py f:\reverse\repable f:\reverse\blutter\work\out_full --rebuild
```

## 验收（Reqable / out_full）

- [x] `asm\` ~1100 文件；含 `PP`/`THR` 重命名与 `; [pp+…] "string"` 注释（约 2k 条）
- [x] `ida_script\addNames.py` ~16MB：`set_name` ~34k、`add_func` ~9.7k；pool 结构注释含 `premium` 等
- [x] 完整分析 exe：`bin\blutter_*_no-compressed-ptrs.exe`（无 `_no-analysis`）

说明：完整 arm64 级 IL 还原未移植；当前以 **asm 注释 + IDA 命名/池结构** 满足桌面 RE 主路径。

## 完成定义

Windows Flutter 桌面包可走完：detect → build VM → dump pool → asm/IDA。
