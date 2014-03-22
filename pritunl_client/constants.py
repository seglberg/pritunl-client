import os
import uuid
import sys
import pkg_resources

LINUX = 'linux'
WIN = 'win'
OSX = 'osx'

if sys.platform == 'linux2':
    PLATFORM = LINUX
elif sys.platform == 'win32':
    PLATFORM = WIN
elif sys.platform == 'darwin':
    PLATFORM = OSX
else:
    raise ValueError('Unknown platform %s' % sys.platform)

CONF_DIR = os.path.expanduser(os.path.join('~', '.config', 'pritunl_client'))
PROFILES_DIR = os.path.join(CONF_DIR, 'profiles')
LINUX_ETC_DIR = os.path.join(os.path.abspath(os.sep), 'etc', 'pritunl_client')
TMP_DIR = os.path.join(os.path.abspath(os.sep), 'tmp')
SOCK_PATH = os.path.join(TMP_DIR, 'pritunl_%s.sock' % uuid.uuid4().hex)
CONNECT_TIMEOUT = 30
OVPN_START_TIMEOUT = 5
OVPN_STOP_TIMEOUT = 5
DAEMON_SOCKET_TIMEOUT = 10

LOGO_DEFAULT_PATH = None
CONNECTED_LOGO_DEFAULT_PATH = None
DISCONNECTED_LOGO_DEFAULT_PATH = None
IMG_ROOTS = [
    os.path.join(os.path.abspath(os.sep), 'usr', 'share', 'pritunl_client'),
    os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'img'),
]

_LOGO_NAME = 'logo.png'
if PLATFORM == LINUX:
    _CONNECTED_LOGO_NAME = 'logo_connected_light.svg'
    _DISCONNECTED_LOGO_NAME = 'logo_disconnected_light.svg'
elif PLATFORM == WIN:
    _CONNECTED_LOGO_NAME = 'logo_connected_win.png'
    _DISCONNECTED_LOGO_NAME = 'logo_disconnected_win.png'
elif PLATFORM == OSX:
    raise NotImplementedError('OSX not supported')
else:
    raise NotImplementedError('Platform not supported')

for img_root in IMG_ROOTS:
    img_path = os.path.join(img_root, 'logo.png')
    if os.path.exists(img_path) and not LOGO_DEFAULT_PATH:
        LOGO_DEFAULT_PATH = img_path
    img_path = os.path.join(img_root, _CONNECTED_LOGO_NAME)
    if os.path.exists(img_path) and not CONNECTED_LOGO_DEFAULT_PATH:
        CONNECTED_LOGO_DEFAULT_PATH = img_path
    img_path = os.path.join(img_root, _DISCONNECTED_LOGO_NAME)
    if os.path.exists(img_path) and not DISCONNECTED_LOGO_DEFAULT_PATH:
        DISCONNECTED_LOGO_DEFAULT_PATH = img_path

SUDO_PASS_FAIL = 'sudo_pass_fail'
CONNECTING = 'connecting'
RECONNECTING = 'reconnecting'
CONNECTED = 'connected'
DISCONNECTED = 'disconnected'
ENDED = 'ended'
