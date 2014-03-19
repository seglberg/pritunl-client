from constants import *
from exceptions import *
from daemon_client import DaemonClient
import os
import uuid
import json
import time
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
        self._start(status_callback, dialog_callback)

    def _start(self, status_callback, dialog_callback=None):
        raise NotImplementedError()

    def stop(self):
        self._stop()

    def _stop(self):
        raise NotImplementedError()

    @classmethod
    def iter_profiles(cls):
        if os.path.isdir(PROFILES_DIR):
            for profile_id in os.listdir(PROFILES_DIR):
                profile_id = profile_id.replace('.ovpn', '')
                yield cls.get_profile(profile_id)

    @classmethod
    def get_profile(cls, id=None):
        from profile_linux import ProfileLinux
        from profile_win import ProfileWin
        from profile_osx import ProfileOsx
        if PLATFORM == LINUX:
            return ProfileLinux(id)
        elif PLATFORM == WIN:
            return ProfileWin(id)
        elif PLATFORM == OSX:
            return ProfileOsx(id)
