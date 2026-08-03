# blutter-windows

[中文文档](README.zh-CN.md) | English

Fork of [worawit/blutter](https://github.com/worawit/blutter) with **Flutter Windows (x64)** support.

Blutter reverse-engineers Flutter apps by compiling a matching Dart AOT runtime and loading the snapshot (`libapp.so` / `app.so`).

| Target | Upstream | This fork |
|--------|----------|-----------|
| Android `libapp.so` (arm64) | Yes | Yes (kept compatible) |
| Flutter Windows (`data/app.so` + `flutter_windows.dll`, x64) | No | **Yes (MVP)** |

**Windows MVP:** detect → build `windows/x64` Dart VM → dump Object Pool → asm comments + IDA rename scripts.

Full x64 IL (parity with arm64) is not ported yet. Port notes: [`work/steps/`](work/steps/README.md).

Works against recent Dart versions only.

## Prebuilt Release (Windows)

If you only need to analyze a Flutter Windows app built with **Dart 3.3.4** / `no-compressed-pointers` (common desktop layout):

1. Download the latest asset from [Releases](https://github.com/1903247335/blutter-windows/releases)
2. Unpack into this repo’s `bin\` (or any folder on `PATH`)
3. Run with Python 3 (still needed for version detection / orchestration):

```powershell
python blutter.py path\to\flutter_app out_dir
```

The zip typically contains:

| File | Role |
|------|------|
| `blutter_dartvm3.3.4_windows_x64_no-compressed-ptrs.exe` | Full MVP analysis (asm + IDA) |
| `blutter_dartvm3.3.4_windows_x64_no-compressed-ptrs_no-analysis.exe` | Faster dump (pool only) |
| `capstone.dll` / `icuuc73.dll` / `icudt73.dll` | Runtime dependencies |

Other Dart versions still require a local build (see below).

## Environment Setup

Requires a recent C++20 toolchain (g++≥13, Clang≥16, or latest MSVC).

### Windows (build from source)

- Git + Python 3
- Visual Studio with “Desktop development with C++” and CMake tools
- Dependencies:

```powershell
python scripts\init_env_win.py
```

- Open **x64 Native Tools Command Prompt** before building

### Debian Unstable (gcc 13)

```bash
apt install python3-pyelftools python3-requests git cmake ninja-build \
    build-essential pkg-config libicu-dev libcapstone-dev
```

### macOS

```bash
brew install cmake ninja pkg-config icu4c capstone
pip3 install pyelftools requests
# Ventura/Sonoma may need: brew install llvm@16
```

## Usage

### Flutter Windows

Point at the install directory (`flutter_windows.dll` + `data/app.so`):

```powershell
python blutter.py path\to\flutter_app out_dir
```

Detect only (no compile / dump):

```powershell
python blutter.py path\to\flutter_app out_dir --detect-only
```

Pool dump without disassembly:

```powershell
python blutter.py path\to\flutter_app out_dir --no-analysis
```

### Android

```bash
python3 blutter.py path/to/app/lib/arm64-v8a out_dir
```

The script reads the Dart version from the engine, builds `blutter` for that VM if missing, then dumps the snapshot.

## Outputs

| Path | Description |
|------|-------------|
| `pp.txt` | Object Pool (strings, types, closures, …) |
| `objs.txt` | Nested object dump |
| `asm/` | Per-library assemblies with PP/THR comments (MVP on x64) |
| `ida_script/` | IDA rename / struct helpers |
| `blutter_frida.js` | Frida script template |

## Directories

| Path | Description |
|------|-------------|
| `bin/` | Built `blutter_dartvm<ver>_<os>_<arch>` binaries |
| `blutter/` | C++ sources (linked against Dart VM) |
| `build/` | CMake build trees (safe to delete) |
| `dartsdk/` | Fetched Dart SDK (safe to delete after build) |
| `packages/` | Prebuilt Dart VM static libs |
| `scripts/` | Fetch / build helpers |
| `work/steps/` | Windows port checklist (this fork) |

## Credit

Original project: [worawit/blutter](https://github.com/worawit/blutter) (MIT).

## TODO

- x64 IL analysis (parity with arm64 `asm2il`)
- Richer argument / return-type recovery
- Better Frida templates
- Obfuscated apps
- iOS binaries
- Direct apk / ipa input
