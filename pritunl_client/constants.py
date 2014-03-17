import os
import uuid

CONF_DIR = os.path.expanduser('~/.config/pritunl')
PROFILES_DIR = os.path.join(CONF_DIR, 'profiles')
LOGS_DIR = os.path.join(CONF_DIR, 'logs')
SOCK_PATH = '/tmp/pritunl_%s.sock' % uuid.uuid4().hex
CONNECT_TIMEOUT = 30
OVPN_START_TIMEOUT = 5
OVPN_STOP_TIMEOUT = 5
DAEMON_SOCKET_TIMEOUT = 10
