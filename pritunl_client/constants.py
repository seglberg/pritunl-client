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

CONF_DIR = os.path.expanduser(os.path.join('~', '.config', 'pritunl'))
PROFILES_DIR = os.path.join(CONF_DIR, 'profiles')
TMP_DIR = os.path.join(os.path.abspath(os.sep), 'tmp')
SOCK_PATH = os.path.join(TMP_DIR, 'pritunl_%s.sock' % uuid.uuid4().hex)
CONNECT_TIMEOUT = 30
OVPN_START_TIMEOUT = 5
OVPN_STOP_TIMEOUT = 5
DAEMON_SOCKET_TIMEOUT = 10

IMG_ROOT = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'img')
LOGO = os.path.join(IMG_ROOT, 'logo.png')
if PLATFORM == WIN:
    CONNECTED_LOGO = os.path.join(IMG_ROOT, 'logo_win.png')
    DISCONNECTED_LOGO = os.path.join(IMG_ROOT, 'logo_disconnected_win.png')
else:
    CONNECTED_LOGO = os.path.join(IMG_ROOT, 'logo_connected_light.svg')
    DISCONNECTED_LOGO = os.path.join(IMG_ROOT, 'logo_disconnected_light.svg')

SUDO_PASS_FAIL = 'sudo_pass_fail'
CONNECTING = 'connecting'
RECONNECTING = 'reconnecting'
CONNECTED = 'connected'
DISCONNECTED = 'disconnected'
ENDED = 'ended'
