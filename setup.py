from pritunl_client.constants import *
from setuptools import setup
import os
import pritunl_client

data_files = []

if PLATFORM == LINUX:
    data_files += [
        (os.path.join(os.path.abspath(os.sep), 'usr', 'share',
                'pritunl_client'), [
            os.path.join('img', 'logo.png'),
            os.path.join('img', 'logo_connected_dark.svg'),
            os.path.join('img', 'logo_disconnected_dark.svg'),
            os.path.join('img', 'logo_connected_light.svg'),
            os.path.join('img', 'logo_disconnected_light.svg'),
        ]),
        (os.path.join(os.path.abspath(os.sep), 'usr', 'share', 'icons',
            'hicolor', '16x16', 'apps'), [os.path.join(
            'img', '16x16', 'pritunl_client.png')]),
        (os.path.join(os.path.abspath(os.sep), 'usr', 'share', 'icons',
            'hicolor', '20x20', 'apps'), [os.path.join(
            'img', '20x20', 'pritunl_client.png')]),
        (os.path.join(os.path.abspath(os.sep), 'usr', 'share', 'icons',
            'hicolor', '22x22', 'apps'), [os.path.join(
            'img', '22x22', 'pritunl_client.png')]),
        (os.path.join(os.path.abspath(os.sep), 'usr', 'share', 'icons',
            'hicolor', '24x24', 'apps'), [os.path.join(
            'img', '24x24', 'pritunl_client.png')]),
        (os.path.join(os.path.abspath(os.sep), 'usr', 'share', 'icons',
            'hicolor', '32x32', 'apps'), [os.path.join(
            'img', '32x32', 'pritunl_client.png')]),
        (os.path.join(os.path.abspath(os.sep), 'usr', 'share', 'icons',
            'hicolor', '36x36', 'apps'), [os.path.join(
            'img', '36x36', 'pritunl_client.png')]),
        (os.path.join(os.path.abspath(os.sep), 'usr', 'share', 'icons',
            'hicolor', '40x40', 'apps'), [os.path.join(
            'img', '40x40', 'pritunl_client.png')]),
        (os.path.join(os.path.abspath(os.sep), 'usr', 'share', 'icons',
            'hicolor', '48x48', 'apps'), [os.path.join(
            'img', '48x48', 'pritunl_client.png')]),
        (os.path.join(os.path.abspath(os.sep), 'usr', 'share', 'icons',
            'hicolor', '64x64', 'apps'), [os.path.join(
            'img', '64x64', 'pritunl_client.png')]),
        (os.path.join(os.path.abspath(os.sep), 'usr', 'share', 'icons',
            'hicolor', '72x72', 'apps'), [os.path.join(
            'img', '72x72', 'pritunl_client.png')]),
        (os.path.join(os.path.abspath(os.sep), 'usr', 'share', 'icons',
            'hicolor', '96x96', 'apps'), [os.path.join(
            'img', '96x96', 'pritunl_client.png')]),
        (os.path.join(os.path.abspath(os.sep), 'usr', 'share', 'icons',
            'hicolor', '128x128', 'apps'), [os.path.join(
            'img', '128x128', 'pritunl_client.png')]),
        (os.path.join(os.path.abspath(os.sep), 'usr', 'share', 'icons',
            'hicolor', '160x160', 'apps'), [os.path.join(
            'img', '160x160', 'pritunl_client.png')]),
        (os.path.join(os.path.abspath(os.sep), 'usr', 'share', 'icons',
            'hicolor', '192x192', 'apps'), [os.path.join(
            'img', '192x192', 'pritunl_client.png')]),
        (os.path.join(os.path.abspath(os.sep), 'usr', 'share', 'icons',
            'hicolor', '256x256', 'apps'), [os.path.join(
            'img', '256x256', 'pritunl_client.png')]),
        (os.path.join(os.path.abspath(os.sep), 'usr', 'share', 'icons',
            'hicolor', '384x384', 'apps'), [os.path.join(
            'img', '384x384', 'pritunl_client.png')]),
        (os.path.join(os.path.abspath(os.sep), 'usr', 'share', 'icons',
            'hicolor', '512x512', 'apps'), [os.path.join(
            'img', '512x512', 'pritunl_client.png')]),
        (os.path.join(os.path.abspath(os.sep), 'usr', 'share', 'icons',
            'hicolor', 'scalable', 'apps'), [os.path.join(
            'img', 'scalable', 'pritunl_client.svg')]),
        (os.path.join(os.path.abspath(os.sep), 'usr', 'share',
            'applications'), [os.path.join(
            'data', 'linux', 'applications', 'pritunl_client.desktop')]),
    ]
elif PLATFORM == WIN:
    import gtk
    import py2exe
    GTK_BASE_PATH = sys.modules['gtk'].__path__[0]
    data_files += [
        ('img', [
            os.path.join('img', 'logo.png'),
            os.path.join('img', 'logo_connected_win.png'),
            os.path.join('img', 'logo_disconnected_win.png'),
        ]),
        (os.path.join('etc', 'gtk-2.0'), [
            os.path.join('data', 'win', 'etc', 'gtkrc')]),
        (os.path.join('share', 'themes', 'MS-Windows', 'gtk-2.0'), [
            os.path.join('data', 'win', 'theme', 'gtkrc')]),
        (os.path.join('lib', 'gtk-2.0', '2.10.0', 'engines'), [
            os.path.join(GTK_BASE_PATH, '..', 'runtime', 'lib', 'gtk-2.0',
                '2.10.0', 'engines', 'libpixmap.dll'),
            os.path.join(GTK_BASE_PATH, '..', 'runtime', 'lib', 'gtk-2.0',
                '2.10.0', 'engines', 'libsvg.dll'),
            os.path.join(GTK_BASE_PATH, '..', 'runtime', 'lib', 'gtk-2.0',
                '2.10.0', 'engines', 'libwimp.dll'),
        ]),
    ]

setup(
    name='pritunl_client',
    version=pritunl_client.__version__,
    description='Pritunl openvpn client',
    long_description=open('README.rst').read(),
    author='Zachary Huff',
    author_email='zach.huff.386@gmail.com',
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
    windows = [{
        'script': 'win_main.py',
    }],
    options = {
        'py2exe': {
            'packages':'encodings',
            'includes': 'cairo, pango, pangocairo, atk, gobject, ' + \
                'gio, gtk.keysyms, rsvg',
        },
    },
)
