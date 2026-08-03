# Step 03 — 加载快照并 dump Object Pool

## 目标

用 windows/x64 VM **加载** `app.so`（不执行业务），导出：

- `pp.txt`
- `objs.txt`
- （可选）`ida_script\`

本步使用 `--no-analysis`（跳过 x64 反汇编）。

## 本步已落地的改动

- `ElfHelper`：整文件 `VirtualAlloc` + `PAGE_EXECUTE_READWRITE`（snapshot `.text` 需可执行）
- `DartApp::finalizeFunctionsInfo`：父函数临时存的是 tagged `FunctionPtr`（null≈1），不能当 C++ 指针判空

## 操作

```powershell
cd f:\reverse\blutter
cmd /c "call `"C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars64.bat`" && set PATH=f:\reverse\blutter\bin;%PATH% && python -u blutter.py f:\reverse\repable f:\reverse\blutter\work\out_pp --no-analysis"
```

## 验收（Reqable）

```powershell
python -c "from pathlib import Path; pp=Path(r'f:/reverse/blutter/work/out_pp/pp.txt').read_text(encoding='utf-8',errors='ignore');
print('premium', pp.lower().count('premium')); print('reqable', pp.lower().count('reqable'))"
```

- [x] 进程退出码 0
- [x] `pp.txt` 非空（约 7.5MB）
- [x] pool 中可见 `premium` / `account` / `reqable` 等字符串
- [x] 另有 `objs.txt`、`asm\`（仅函数头）、`ida_script\`、`blutter_frida.js`

## 下一跳

[04-x64-analyzer.md](04-x64-analyzer.md)
