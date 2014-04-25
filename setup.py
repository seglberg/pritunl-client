from pritunl_client.constants import *
from setuptools import setup
import os
import pritunl_client

data_files = []

if PLATFORM == LINUX:
    for img_size in os.listdir(os.path.join('img', 'hicolor')):
        for img_name in os.listdir(os.path.join('img', 'hicolor', img_size)):
            data_files.append((os.path.join(os.path.abspath(os.sep), 'usr',
                'share', 'icons', 'hicolor', img_size, 'apps'), [os.path.join(
                'img', 'hicolor', img_size, img_name)]))

    for img_theme in ('ubuntu-mono-dark', 'ubuntu-mono-light'):
        for img_size in os.listdir(os.path.join('img', img_theme)):
            for img_name in os.listdir(os.path.join('img', img_theme,
                    img_size)):
                data_files.append((os.path.join(os.path.abspath(os.sep), 'usr',
                    'share', 'icons', img_theme, 'apps', img_size), [
                    os.path.join('img', img_theme, img_size, img_name)]))

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
            'data', 'linux', 'applications', 'pritunl_client.desktop')]),
        (os.path.join(os.path.abspath(os.sep), 'etc', 'xdg', 'autostart'),
            [os.path.join('data', 'linux', 'applications',
                'pritunl_client.desktop')]),
        (os.path.join(os.path.abspath(os.sep), 'usr', 'share', 'polkit-1',
            'actions'), [os.path.join('data', 'linux', 'polkit',
            'com.pritunl.client.policy')]),
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

setup(
    name='pritunl_client',
    version=pritunl_client.__version__,
    description='Pritunl openvpn client',
    long_description=open('README.rst').read(),
    author='Pritunl',
    author_email='contact@pritunl.com',
    url='https://github.com/pritunl/pritunl-client',
    download_url='https://github.com/pritunl/pritunl-client/archive/' + \
        '%s.tar.gz' % pritunl_client.__version__,
    keywords='pritunl, openvpn, vpn, management, client',
    packages=['pritunl_client'],
    license=open('LICENSE').read(),
    zip_safe=False,
    data_files=data_files,
    entry_points={
        'console_scripts': [
            'pritunl_client = pritunl_client.__main__:client',
            'pritunl_client_pk = pritunl_client.__main__:pk',
        ],
    },
    platforms=[
        'Linux',
        'Windows',
        'MacOS',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: X11 Applications :: GTK',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU Affero General Public License v3',
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
