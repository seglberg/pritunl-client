from constants import *
import os
import uuid
import json
import time
import subprocess
import threading

_connections = {}

class Profile:
    def __init__(self, id=None):
        if id:
            self.id = id
        else:
            self.id = uuid.uuid4()
        self._loaded = False

        self.user_name = None
        self.org_name = None
        self.server_name = None

        if not os.path.isdir(PROFILES_DIR):
            os.makedirs(PROFILES_DIR)

        self.path = os.path.join(PROFILES_DIR, '%s.ovpn' % self.id)

        if id:
            self.load()

    def __getattr__(self, name):
        if name in ('user_name', 'org_name', 'server_name'):
            self._load()
        elif name == 'status':
            connection_data = _connections.get(self.id)
            if connection_data:
                return connection_data.get('status', False)
            return False
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

    def start(self, status_callback, dialog_callback):
        process = subprocess.Popen(['gksudo', 'openvpn %s' % self.path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        data = {
            'status': False,
            'process': process,
            'status_callback': status_callback,
            'dialog_callback': dialog_callback,
        }
        _connections[self.id] = data

        def change_status(status):
            data['status'] = status
            if data['dialog_callback']:
                callback = data['dialog_callback']
                data['dialog_callback'] = None
                gobject.idle_add(callback, self)
            gobject.idle_add(data['status_callback'], self)

        def poll_thread():
            while True:
                line = process.stdout.readline()
                print line.strip()
                if not line:
                    if process.poll() is not None:
                        break
                    else:
                        continue
                if 'Initialization Sequence Completed' in line:
                    change_status(True)
                elif 'Inactivity timeout' in line:
                    change_status(False)
            change_status(False)
            data.pop(self.id, None)

        def dialog_thread():
            time.sleep(CONNECT_TIMEOUT)
            if not data['dialog_callback']:
                return
            self.stop()

        thread = threading.Thread(target=poll_thread)
        thread.daemon = True
        thread.start()

        thread = threading.Thread(target=dialog_thread)
        thread.daemon = True
        thread.start()

    def stop(self):
        connection_data = _connections.get(self.id)
        if connection_data:
            process = connection_data.get('process')
            if process:
                process.terminate()
                for i in xrange(int(OVPN_EXIT_TIMEOUT / 0.1)):
                    time.sleep(0.1)
                    if process.poll() is not None:
                        break
                    process.terminate()
                if process.poll() is not None:
                    return

                process.kill()
                for i in xrange(int(OVPN_EXIT_TIMEOUT / 0.1)):
                    time.sleep(0.1)
                    if process.poll() is not None:
                        break
                    process.kill()

    @classmethod
    def iter_profiles(cls):
        if os.path.isdir(PROFILES_DIR):
            for profile_id in os.listdir(PROFILES_DIR):
                profile_id = profile_id.replace('.ovpn', '')
                yield Profile(profile_id)
