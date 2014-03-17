import os
import uuid
import sys
import pkg_resources

CONF_DIR = os.path.expanduser(os.path.join('~', '.config', 'pritunl'))
PROFILES_DIR = os.path.join(CONF_DIR, 'profiles')
TMP_DIR = os.path.join(os.path.abspath(os.sep), 'tmp')
SOCK_PATH = os.path.join(TMP_DIR, 'pritunl_%s.sock' % uuid.uuid4().hex)
CONNECT_TIMEOUT = 30
OVPN_START_TIMEOUT = 5
OVPN_STOP_TIMEOUT = 5
DAEMON_SOCKET_TIMEOUT = 10

CONNECTED_LOGO_DARK = pkg_resources.resource_filename(__name__,
    os.path.join('..', 'img', 'logo_dark.svg'))
DISCONNECTED_LOGO_DARK = pkg_resources.resource_filename(__name__,
    os.path.join('..', 'img', 'logo_disconnected_dark.svg'))
CONNECTED_LOGO_LIGHT = pkg_resources.resource_filename(__name__,
    os.path.join('..', 'img', 'logo_light.svg'))
DISCONNECTED_LOGO_LIGHT = pkg_resources.resource_filename(__name__,
    os.path.join('..', 'img', 'logo_disconnected_light.svg'))

SUDO_PASS_FAIL = 'sudo_pass_fail'
CONNECTING = 'connecting'
RECONNECTING = 'reconnecting'
CONNECTED = 'connected'
DISCONNECTED = 'disconnected'
ENDED = 'ended'

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
