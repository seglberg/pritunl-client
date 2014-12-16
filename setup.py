from setuptools import setup
import os
import sys
import copy
import shutil
import fileinput
import shlex

VERSION = '1.0.460.45'
PATCH_DIR = 'build'
install_upstart = True
install_systemd = True
install_gtk = True
data_files = []

LINUX = 'linux'
SHELL = 'shell'
WIN = 'win'
OSX = 'osx'

if sys.platform.startswith('linux'):
    PLATFORM = LINUX
elif sys.platform == 'win32':
    PLATFORM = WIN
elif sys.platform == 'darwin':
    PLATFORM = OSX

prefix = sys.prefix
for arg in copy.copy(sys.argv):
    if arg.startswith('--prefix'):
        prefix = os.path.normpath(shlex.split(arg)[0].split('=')[-1])
    elif arg == '--no-upstart':
        sys.argv.remove('--no-upstart')
        install_upstart = False
    elif arg == '--no-systemd':
        sys.argv.remove('--no-systemd')
        install_systemd = False
    elif arg == '--no-gtk':
        sys.argv.remove('--no-gtk')
        install_gtk = False

if not os.path.exists('build'):
    os.mkdir('build')

if PLATFORM == LINUX:
    if install_gtk:
        for img_size in os.listdir(os.path.join('img', 'hicolor')):
            for img_name in os.listdir(os.path.join('img', 'hicolor',
                    img_size)):
                data_files.append((os.path.join(os.path.abspath(os.sep), 'usr',
                    'share', 'icons', 'hicolor', img_size, 'apps'), [
                        os.path.join('img', 'hicolor', img_size, img_name)]))

        for img_theme in ('ubuntu-mono-dark', 'ubuntu-mono-light'):
            for img_size in os.listdir(os.path.join('img', img_theme)):
                for img_name in os.listdir(os.path.join('img', img_theme,
                        img_size)):
                    data_files.append((os.path.join(os.path.abspath(os.sep),
                        'usr', 'share', 'icons', img_theme, 'apps', img_size),
                        [os.path.join('img', img_theme, img_size, img_name)]))

        data_files += [
            (os.path.join(os.path.abspath(os.sep), 'usr', 'share',
                    'pritunl_client'), [
                os.path.join('img', 'logo.png'),
                os.path.join('img', 'logo_connected_dark.svg'),
                os.path.join('img', 'logo_disconnected_dark.svg'),
                os.path.join('img', 'logo_connected_light.svg'),
                os.path.join('img', 'logo_disconnected_light.svg'),
            ]),
            (os.path.join(os.path.abspath(os.sep), 'usr', 'share',
                'applications'), [os.path.join(
                    'data', 'linux', 'applications',
                    'pritunl-client-gtk.desktop')]),
            (os.path.join(os.path.abspath(os.sep), 'etc', 'xdg', 'autostart'),
                [os.path.join('data', 'linux', 'applications',
                    'pritunl-client-gtk.desktop')]),
            (os.path.join(os.path.abspath(os.sep), 'usr', 'share', 'polkit-1',
                'actions'), [os.path.join('data', 'linux', 'polkit',
                'com.pritunl.client.policy')]),
        ]

    data_files += [
        (os.path.join(os.path.abspath(os.sep), 'var', 'log'), [
            os.path.join('data', 'var', 'pritunl-client.log'),
            os.path.join('data', 'var', 'pritunl-client.log.1'),
        ]),
    ]

elif PLATFORM == WIN:
    try:
        try:
            import py2exe.mf as modulefinder
        except ImportError:
            import modulefinder
        import sys
        import win32com
        for path in win32com.__path__[1:]:
            modulefinder.AddPackagePath('win32com', path)
        __import__('win32com.shell')
        module = sys.modules['win32com.shell']
        for path in module.__path__[1:]:
            modulefinder.AddPackagePath('win32com.shell', path)
    except ImportError:
        pass

    import wx
    import py2exe
    data_files += [
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

console_scripts = [
    'pritunl-client = pritunl_client.__main__:client_shell',
]

if install_gtk:
    console_scripts += [
        'pritunl-client-gtk = pritunl_client.__main__:client_gui',
        'pritunl-client-pk-start = pritunl_client.__main__:pk_start',
        'pritunl-client-pk-autostart = ' + \
            'pritunl_client.__main__:pk_autostart',
        'pritunl-client-pk-stop = pritunl_client.__main__:pk_stop',
        'pritunl-client-pk-set-autostart = ' + \
            'pritunl_client.__main__:pk_set_autostart',
        'pritunl-client-pk-clear-autostart = ' + \
            'pritunl_client.__main__:pk_clear_autostart',
    ]

patch_files = []
if install_upstart:
    patch_files.append('%s/pritunl-client.conf' % PATCH_DIR)
    data_files.append(('/etc/init', ['%s/pritunl-client.conf' % PATCH_DIR]))
    data_files.append(('/etc/init.d', ['data/init.d/pritunl-client.sh']))
    shutil.copy('data/init/pritunl-client.conf',
        '%s/pritunl-client.conf' % PATCH_DIR)
if install_systemd:
    patch_files.append('%s/pritunl-client.service' % PATCH_DIR)
    data_files.append(('/etc/systemd/system',
        ['%s/pritunl-client.service' % PATCH_DIR]))
    shutil.copy('data/systemd/pritunl-client.service',
        '%s/pritunl-client.service' % PATCH_DIR)

for file_name in patch_files:
    for line in fileinput.input(file_name, inplace=True):
        line = line.replace('%PREFIX%', prefix)
        print line.rstrip('\n')

setup(
    name='pritunl_client',
    version=VERSION,
    description='Pritunl VPN Client',
    long_description=open('README.rst').read(),
    author='Pritunl',
    author_email='contact@pritunl.com',
    url='https://github.com/pritunl/pritunl-client',
    download_url='https://github.com/pritunl/pritunl-client/archive/' + \
        '%s.tar.gz' % VERSION,
    keywords='pritunl, openvpn, vpn, management, client',
    packages=[
        'pritunl_client',
        'pritunl_client.click',
    ],
    license=open('LICENSE').read(),
    zip_safe=False,
    data_files=data_files,
    entry_points={
        'console_scripts': console_scripts,
    },
    platforms=[
        'Linux',
        'Windows',
        'MacOS',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: X11 Applications :: GTK',
        'Intended Audience :: End Users/Desktop',
        'License :: Other/Proprietary License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Networking',
    ],
    windows=[{
        'script': 'win_main.py',
        'dest_base': 'pritunl_client',
        'icon_resources': [(1, 'img/logo.ico')],
    },
    {
        'script': 'win_main_clean.py',
        'dest_base': 'pritunl_client_clean',
        'icon_resources': [(1, 'img/logo.ico')],
    }],
    options = {
        'py2exe': {
            'packages':'encodings',
            'includes': 'cairo, pango, pangocairo, atk, gobject, ' + \
                'gio, gtk.keysyms, rsvg',
            'dll_excludes': ['w9xpopen.exe'],
        },
    },
)
