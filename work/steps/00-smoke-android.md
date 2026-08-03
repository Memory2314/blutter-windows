# Step 00 — 安卓原版冒烟

## 目标

确认本机可编译/运行 **upstream 安卓 arm64** 路径，避免后面 Win 移植被环境问题误导。

## 前置

- Visual Studio（含 C++ / CMake）
- 在 **x64 Native Tools Command Prompt** 中操作
- 任意含 `lib/arm64-v8a/libapp.so` + `libflutter.so` 的 Flutter APK

## 操作

```powershell
cd f:\reverse\blutter
python scripts\init_env_win.py

# 解出 APK 后：
python blutter.py <arm64-v8a目录> f:\reverse\blutter\work\out_android_smoke --no-analysis
```

## 验收

- [ ] 无报错结束
- [ ] 输出目录存在 `pp.txt` / `objs.txt`
- [ ] `bin\` 下出现 `blutter_dartvm*_android_arm64*.exe`

## 失败时

先不要改 Win 代码；修 VS / ICU / Capstone / 网络拉 Dart SDK。

## 下一跳

[01-detect-windows-input.md](01-detect-windows-input.md)
