from constants import *
from exceptions import *
from daemon_client import DaemonClient
import os
import uuid
import json
import time
import subprocess
import threading
import signal
import socket
import gtk
import gobject

_connections = {}

class Profile:
    def __init__(self, id=None):
        if id:
            self.id = id
        else:
            self.id = uuid.uuid4().hex
        self._loaded = False

        self.user_name = None
        self.org_name = None
        self.server_name = None

        if not os.path.isdir(PROFILES_DIR):
            os.makedirs(PROFILES_DIR)

        self.working_dir = PROFILES_DIR
        self.path = os.path.join(PROFILES_DIR, '%s.ovpn' % self.id)

        if id:
            self.load()

    def __getattr__(self, name):
        if name in ('user_name', 'org_name', 'server_name'):
            self._load()
        elif name == 'status':
            connection_data = _connections.get(self.id)
            if connection_data:
                return connection_data.get('status', ENDED)
            return ENDED
        elif name not in self.__dict__:
            raise AttributeError('Config instance has no attribute %r' % name)
        return self.__dict__[name]

    def load(self):
        self.user_name = None
        self.org_name = None
        self.server_name = None

        with open(self.path, 'r') as profile_file:
            info_str = profile_file.readline().replace('#', '', 1).strip()
            try:
                info_data = json.loads(info_str)
            except ValueError:
                return
            if 'user' in info_data:
                self.user_name = info_data['user']
            if 'organization' in info_data:
                self.org_name = info_data['organization']
            if 'server' in info_data:
                self.server_name = info_data['server']

    def write(self, data):
        with open(self.path, 'w') as profile_file:
            profile_file.write(data)

    def _set_status(self, status, dialog_error=None):
        data = _connections.get(self.id)
        if not data:
            return
        data['status'] = status
        callback = data.get('dialog_callback')
        if callback:
            data['dialog_callback'] = None
            gobject.idle_add(callback, dialog_error)

        callback = data.get('status_callback')
        if callback:
            gobject.idle_add(callback)

    def start(self, status_callback, dialog_callback=None):
        if self.status not in (DISCONNECTED, ENDED):
            # TODO
            print 'INVALID STATE'
            return
        self._linux_start(status_callback, dialog_callback)

    def _linux_start(self, status_callback, dialog_callback):
        data = {
            'status': CONNECTING,
            'process': None,
            'status_callback': status_callback,
            'dialog_callback': dialog_callback,
        }
        _connections[self.id] = data
        log_path = os.path.join(TMP_DIR, 'pritunl_%s.log' % self.id)

        client = DaemonClient()
        try:
            client.start_conn(self.id, self.working_dir, self.path, log_path)
        except SudoPassFail:
            self._set_status(ENDED, SUDO_PASS_FAIL)
            return
        except SudoCancel:
            self._set_status(ENDED)
            return

        for i in xrange(int(OVPN_START_TIMEOUT / 0.1)):
            time.sleep(0.1)
            if os.path.exists(log_path):
                break
        if not os.path.exists(log_path):
            self.stop()

        def poll_thread():
            process = subprocess.Popen(['tail', '-c', '+1',
                '--follow=name', log_path], stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            data['process'] = process
            while True:
                line = process.stdout.readline()
                if not line:
                    if process.poll() is not None:
                        break
                    else:
                        continue
                print line.strip()
                if 'Initialization Sequence Completed' in line:
                    self._set_status(CONNECTED)
                elif 'Inactivity timeout' in line:
                    self._set_status(RECONNECTING)
            self._set_status(DISCONNECTED)

        def dialog_thread():
            time.sleep(CONNECT_TIMEOUT)
            if not data.get('dialog_callback'):
                return
            self.stop()

        thread = threading.Thread(target=poll_thread)
        thread.daemon = True
        thread.start()

        thread = threading.Thread(target=dialog_thread)
        thread.daemon = True
        thread.start()

    def stop(self):
        self._linux_stop()

    def _linux_stop(self):
        client = DaemonClient()
        client.stop_conn(self.id)

        data = _connections.get(self.id)
        if data:
            process = data.get('process')
            if process:
                process.kill()

        self._set_status(ENDED)

    @classmethod
    def iter_profiles(cls):
        if os.path.isdir(PROFILES_DIR):
            for profile_id in os.listdir(PROFILES_DIR):
                profile_id = profile_id.replace('.ovpn', '')
                yield Profile(profile_id)
