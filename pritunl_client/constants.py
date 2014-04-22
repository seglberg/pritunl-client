import os
import uuid
import sys
import pkg_resources

APP_NAME = 'pritunl_client'
APP_NAME_FORMATED = 'Pritunl Client'

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

CONF_DIR = os.path.expanduser(os.path.join('~', '.config', APP_NAME))
PROFILES_DIR = os.path.join(CONF_DIR, 'profiles')
LINUX_ETC_DIR = os.path.join(os.path.abspath(os.sep), 'etc', APP_NAME)
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
    os.path.join(os.path.abspath(os.sep), 'usr', 'share', APP_NAME),
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
    _CONNECTED_LOGO_NAME = 'logo_connected_osx.png'
    _DISCONNECTED_LOGO_NAME = 'logo_disconnected_osx.png'
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

if PLATFORM == WIN:
    WIN_OPENVPN_PATH = None
    for path in (
                os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])),
                    'openvpn', 'openvpn.exe'),
                os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])),
                    'data', 'win', 'openvpn', 'openvpn.exe'),
            ):
        if os.path.isfile(path):
            WIN_OPENVPN_PATH = path
    if not WIN_OPENVPN_PATH:
        raise ValueError('Failed to find openvpn executable')

    WIN_TUNTAP_DIR = None
    for path in (
                os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])),
                    'tuntap'),
                os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])),
                    'data', 'win', 'tuntap'),
            ):
        if os.path.exists(path):
            WIN_TUNTAP_DIR = path
    if not WIN_TUNTAP_DIR:
        raise ValueError('Failed to find tuntap directory')

CONNECTING = 'connecting'
RECONNECTING = 'reconnecting'
CONNECTED = 'connected'
ENDED = 'ended'
ERROR = 'error'
AUTH_ERROR = 'auth_error'
TIMEOUT_ERROR = 'timeout_error'
ACTIVE_STATES = set([CONNECTING, RECONNECTING, CONNECTED])
INACTIVE_STATES = set([ENDED, ERROR, AUTH_ERROR, TIMEOUT_ERROR])
ERROR_STATES = set([ERROR, AUTH_ERROR, TIMEOUT_ERROR])

START = 'start'
AUTOSTART = 'autostart'

BUTTONS_OK = 'buttons_ok'
BUTTONS_CANCEL = 'buttons_cancel'
BUTTONS_OK_CANCEL = 'buttons_ok_cancel'

MESSAGE_INFO = 'message_info'
MESSAGE_QUESTION = 'message_question'
MESSAGE_ERROR = 'message_error'
MESSAGE_LOADING = 'message_loading'
