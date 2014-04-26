# -*- mode: python -*-
import os
import subprocess
import shutil

DIST_PATH = 'dist'

data_files = [
    ('img', [
        os.path.join('img', 'logo.png'),
        os.path.join('img', 'logo_connected_win.png'),
        os.path.join('img', 'logo_disconnected_win.png'),
    ]),
    ('tuntap', [
        os.path.join('data', 'win', 'tuntap', 'devcon.exe'),
        os.path.join('data', 'win', 'tuntap', 'OemWin2k.inf'),
        os.path.join('data', 'win', 'tuntap', 'tap0901.cat'),
        os.path.join('data', 'win', 'tuntap', 'tap0901.sys'),
    ]),
    ('openvpn', [
        os.path.join('data', 'win', 'openvpn', 'libeay32.dll'),
        os.path.join('data', 'win', 'openvpn', 'liblzo2-2.dll'),
        os.path.join('data', 'win', 'openvpn', 'libpkcs11-helper-1.dll'),
        os.path.join('data', 'win', 'openvpn', 'openvpn.exe'),
        os.path.join('data', 'win', 'openvpn', 'ssleay32.dll'),
    ]),
]

if os.path.exists(DIST_PATH):
    shutil.rmtree(DIST_PATH)
os.makedirs(DIST_PATH)

for dest_dir, files in data_files:
    os.makedirs(os.path.join(DIST_PATH, dest_dir))
    for file_path in files:
        shutil.copy(file_path, os.path.join(DIST_PATH, dest_dir,
            os.path.basename(file_path)))


a = Analysis(
    ['win_main.py'],
    pathex=['C:\\Users\\windows\\Desktop\\pritunl-client'],
    hiddenimports=[],
    hookspath=None,
    runtime_hooks=None,
)
for data in a.datas:
    if 'pyconfig' in data[0]:
        a.datas.remove(data)
        break
pyz = PYZ(
    a.pure,
)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='pritunl_client.exe',
    debug=False,
    strip=None,
    upx=True,
    console=False,
    icon='img\\logo.ico',
)
