# blutter-windows

Fork of [worawit/blutter](https://github.com/worawit/blutter) with **Flutter Windows (x64)** support.

Blutter reverse-engineers Flutter apps by compiling a matching Dart AOT runtime and loading the snapshot (`libapp.so` / `app.so`).

| Target | Upstream | This fork |
|--------|----------|-----------|
| Android `libapp.so` (arm64) | Yes | Yes (kept compatible) |
| Flutter Windows (`data/app.so` + `flutter_windows.dll`, x64) | No | **Yes (MVP)** |

Windows MVP: detect → build `windows/x64` Dart VM → dump Object Pool → asm comments + IDA rename scripts.  
Full x64 IL (parity with arm64) is not ported yet. See `work/steps/README.md` for the port checklist.

Works against recent Dart versions only. High-priority gaps: [TODO](#todo).

## Environment Setup
This application uses C++20 Formatting library. It requires very recent C++ compiler such as g++>=13, Clang>=16.

I recommend using Linux OS (only tested on Deiban sid/trixie) because it is easy to setup.

### Debian Unstable (gcc 13)
**_NOTE:_**
Use ONLY Debian/Ubuntu version that provides gcc>=13 from its own main repository.
Using ported gcc to old Debian/Ubuntu version does not work.

- Install build tools and depenencies
```
apt install python3-pyelftools python3-requests git cmake ninja-build \
    build-essential pkg-config libicu-dev libcapstone-dev
```

### Windows
- Install git and python 3
- Install latest Visual Studio with "Desktop development with C++" and "C++ CMake tools"
- Install required libraries (libcapstone and libicu4c)
```
python scripts\init_env_win.py
```
- Start "x64 Native Tools Command Prompt"

### macOS Sequoia
- Install XCode
- Install required tools
```
brew install cmake ninja pkg-config icu4c capstone
pip3 install pyelftools requests
```

### macOS Ventura and Sonoma (clang 16)
- Install XCode
- Install clang 16 and required tools
```
brew install llvm@16 cmake ninja pkg-config icu4c capstone
pip3 install pyelftools requests
```

## Usage

### Android
Extract "lib" directory from apk file
```
python3 blutter.py path/to/app/lib/arm64-v8a out_dir
```

### Flutter Windows
Point at the app install directory (contains `flutter_windows.dll` and `data/app.so`):
```
python blutter.py path\to\flutter_app out_dir
```
Detect only (no build):
```
python blutter.py path\to\flutter_app out_dir --detect-only
```

The script detects the Dart version from the Flutter engine, builds `blutter` for that VM if needed, then dumps info from the AOT snapshot.

## Update
You can use ```git pull``` to update and run blutter.py with ```--rebuild``` option to force rebuild the executable
```
python3 blutter.py path/to/app/lib/arm64-v8a out_dir --rebuild
```

## Output files
- **asm/\*** libapp assemblies with symbols
- **blutter_frida.js** the frida script template for the target application
- **objs.txt** complete (nested) dump of Object from Object Pool
- **pp.txt** all Dart objects in Object Pool
- **ida_script/** IDA rename / struct helper scripts


## Directories
- **bin** contains blutter executables for each Dart version in "blutter_dartvm\<ver\>\_\<os\>\_\<arch\>" format
- **blutter** contains source code. need building against Dart VM library
- **build** contains building projects which can be deleted after finishing the build process
- **dartsdk** contains checkout of Dart Runtime which can be deleted after finishing the build process
- **external** contains 3rd party libraries for Windows only
- **packages** contains the static libraries of Dart Runtime
- **scripts** contains python scripts for getting/building Dart
- **work/steps** Windows/x64 port notes (this fork)


## Generating Visual Studio Solution for Development
I use Visual Studio to delevlop Blutter on Windows. ```--vs-sln``` options can be used to generate a Visual Studio solution.
```
python blutter.py path\to\lib\arm64-v8a build\vs --vs-sln
```

## Credit
Original project: [worawit/blutter](https://github.com/worawit/blutter) (MIT).

## TODO
- x64 IL analysis (parity with arm64 `asm2il`)
- More code analysis
  - Function arguments and return type
  - Some psuedo code for code pattern
- Generate better Frida script
  - More internal classes
  - Object modification
- Obfuscated app (still missing many functions)
- Reading iOS binary
- Input as apk or ipa
