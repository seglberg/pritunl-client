import os
import uuid
import sys

CONF_DIR = os.path.expanduser('~/.config/pritunl')
PROFILES_DIR = os.path.join(CONF_DIR, 'profiles')
TMP_DIR = '/tmp'
SOCK_PATH = os.path.join(TMP_DIR, 'pritunl_%s.sock' % uuid.uuid4().hex)
CONNECT_TIMEOUT = 30
OVPN_START_TIMEOUT = 5
OVPN_STOP_TIMEOUT = 5
DAEMON_SOCKET_TIMEOUT = 10

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
