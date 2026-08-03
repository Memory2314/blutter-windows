import io
import os
import re
import requests
import sys
import zipfile
import zlib
from struct import unpack

from elftools.elf.elffile import ELFFile

# TODO: support Mach-O (iOS)


def extract_snapshot_hash_flags(libapp_file):
    with open(libapp_file, 'rb') as f:
        elf = ELFFile(f)
        dynsym = elf.get_section_by_name('.dynsym')
        if dynsym is None:
            # some builds only keep symtab
            dynsym = elf.get_section_by_name('.symtab')
        assert dynsym is not None, 'Cannot find symbol table in libapp/app.so'
        syms = dynsym.get_symbol_by_name('_kDartVmSnapshotData')
        assert syms, 'Cannot find _kDartVmSnapshotData'
        sym = syms[0]
        assert sym['st_size'] > 128
        f.seek(sym['st_value'] + 20)
        snapshot_hash = f.read(32).decode()
        data = f.read(256)
        flags = data[:data.index(b'\0')].decode().strip().split(' ')

    return snapshot_hash, flags


def _arch_os_from_flags(flags):
    """Prefer snapshot flags over engine-file heuristics."""
    arch = None
    os_name = None
    if 'arm64' in flags:
        arch = 'arm64'
    elif 'x64' in flags:
        arch = 'x64'
    elif 'arm' in flags:
        arch = 'arm'
    elif 'ia32' in flags:
        arch = 'ia32'

    if 'android' in flags:
        os_name = 'android'
    elif 'windows' in flags:
        os_name = 'windows'
    elif 'ios' in flags:
        os_name = 'ios'
    elif 'macos' in flags or 'fuchsia' in flags:
        # blutter build scripts historically use limited OS names
        os_name = 'macos' if 'macos' in flags else 'fuchsia'

    return arch, os_name


def _is_pe(path):
    with open(path, 'rb') as f:
        return f.read(2) == b'MZ'


def _is_elf(path):
    with open(path, 'rb') as f:
        return f.read(4) == b'\x7fELF'


def extract_libflutter_info_elf(libflutter_file):
    with open(libflutter_file, 'rb') as f:
        elf = ELFFile(f)
        em = elf.header['e_machine']
        # pyelftools may return int or string depending on version
        if em in ('EM_AARCH64', 183):
            arch = 'arm64'
        elif em in ('EM_X86_64', 62):
            arch = 'x64'
        elif em in ('EM_IA_64', 50):
            # legacy mistaken mapping kept as fallback
            arch = 'x64'
        else:
            assert False, f'Unsupported ELF architecture: {em}'

        section = elf.get_section_by_name('.rodata')
        data = section.data()

        sha_hashes = re.findall(b'\x00([a-f\\d]{40})(?=\x00)', data)
        engine_ids = [h.decode() for h in sha_hashes]
        assert len(engine_ids) >= 1, 'No engine id hashes found in libflutter.so'

        m = re.search(br'\x00([\d\w\.-]+) \((stable|beta|dev)\)', data)
        dart_version = None if m is None else m.group(1).decode()

    return engine_ids, dart_version, arch, 'android'


def extract_libflutter_info_pe(libflutter_file):
    """Parse Flutter Windows engine DLL (PE)."""
    with open(libflutter_file, 'rb') as f:
        data = f.read()

    # engine ids appear as 40-hex digests
    engine_ids = list(dict.fromkeys(
        h.decode() for h in re.findall(br'(?<![0-9a-f])([a-f0-9]{40})(?![0-9a-f])', data)
    ))
    assert engine_ids, 'No engine id hashes found in flutter_windows.dll'

    m = re.search(br'([\d\w\.-]+) \((stable|beta|dev)\)', data)
    dart_version = None if m is None else m.group(1).decode()

    # desktop windows engine is x64 for this fork target
    return engine_ids, dart_version, 'x64', 'windows'


def extract_libflutter_info(libflutter_file):
    if _is_elf(libflutter_file):
        return extract_libflutter_info_elf(libflutter_file)
    if _is_pe(libflutter_file):
        return extract_libflutter_info_pe(libflutter_file)
    assert False, f'Unsupported engine file format: {libflutter_file}'


def get_dart_sdk_url_size(engine_ids, os_name='windows', arch='x64'):
    # Map target OS/arch to flutter infra dart-sdk zip name
    if os_name == 'windows' and arch == 'x64':
        zip_name = 'dart-sdk-windows-x64.zip'
    elif os_name == 'android' and arch == 'arm64':
        # same as upstream path used previously for commit lookup
        zip_name = 'dart-sdk-windows-x64.zip'
    else:
        zip_name = 'dart-sdk-windows-x64.zip'

    for engine_id in engine_ids:
        url = f'https://storage.googleapis.com/flutter_infra_release/flutter/{engine_id}/{zip_name}'
        resp = requests.head(url, timeout=30)
        if resp.status_code == 200:
            sdk_size = int(resp.headers.get('Content-Length', '0'))
            return engine_id, url, sdk_size

    return None, None, None


def get_dart_commit(url):
    commit_id = None
    dart_version = None
    fp = None
    with requests.get(url, headers={'Range': 'bytes=0-4096'}, stream=True, timeout=60) as r:
        if r.status_code // 10 == 20:
            x = next(r.iter_content(chunk_size=4096))
            fp = io.BytesIO(x)

    if fp is not None:
        while fp.tell() < 4096 - 30 and (commit_id is None or dart_version is None):
            _, _, _, compMethod, _, _, _, compressSize, _, filenameLen, extraLen = unpack('<IHHHHHIIIHH', fp.read(30))
            filename = fp.read(filenameLen)
            if extraLen > 0:
                fp.seek(extraLen, io.SEEK_CUR)
            data = fp.read(compressSize)

            assert compMethod == zipfile.ZIP_DEFLATED, 'Unexpected compression method'
            if filename == b'dart-sdk/revision':
                commit_id = zlib.decompress(data, wbits=-zlib.MAX_WBITS).decode().strip()
            elif filename == b'dart-sdk/version':
                dart_version = zlib.decompress(data, wbits=-zlib.MAX_WBITS).decode().strip()

    return commit_id, dart_version


def extract_dart_info(libapp_file: str, libflutter_file: str):
    snapshot_hash, flags = extract_snapshot_hash_flags(libapp_file)

    engine_ids, dart_version, arch_from_engine, os_from_engine = extract_libflutter_info(libflutter_file)
    arch_from_flags, os_from_flags = _arch_os_from_flags(flags)

    arch = arch_from_flags or arch_from_engine
    os_name = os_from_flags or os_from_engine
    assert arch and os_name, f'Cannot determine target arch/os from flags={flags} engine=({arch_from_engine},{os_from_engine})'

    if dart_version is None:
        engine_id, sdk_url, _sdk_size = get_dart_sdk_url_size(engine_ids, os_name, arch)
        assert sdk_url, f'Cannot resolve dart-sdk zip for engine ids: {engine_ids}'
        _commit_id, dart_version = get_dart_commit(sdk_url)
        assert dart_version, f'Cannot read dart version from {sdk_url}'

    return dart_version, snapshot_hash, flags, arch, os_name


def find_windows_pair(indir: str):
    """Return (app.so, flutter_windows.dll) for a Flutter Windows install tree."""
    candidates_app = [
        os.path.join(indir, 'data', 'app.so'),
        os.path.join(indir, 'app.so'),
        os.path.join(indir, 'libapp.so'),
    ]
    candidates_engine = [
        os.path.join(indir, 'flutter_windows.dll'),
        os.path.join(indir, 'libflutter.so'),
        os.path.join(os.path.dirname(indir.rstrip('\\/')), 'flutter_windows.dll'),
    ]

    app = next((p for p in candidates_app if os.path.isfile(p)), None)
    engine = next((p for p in candidates_engine if os.path.isfile(p)), None)
    return app, engine


if __name__ == '__main__':
    libdir = sys.argv[1]
    app, engine = find_windows_pair(libdir)
    if app is None:
        app = os.path.join(libdir, 'libapp.so')
    if engine is None:
        engine = os.path.join(libdir, 'libflutter.so')
    print(extract_dart_info(app, engine))
