from constants import *
from exceptions import *
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

        self.profile_name = None
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
        if name == 'name':
            return self.profile_name or '%s@%s (%s)' % (
                self.user_name, self.org_name, self.server_name)
        elif name == 'status':
            connection_data = _connections.get(self.id)
            if connection_data:
                return connection_data.get('status', ENDED)
            return ENDED
        elif name not in self.__dict__:
            raise AttributeError('Config instance has no attribute %r' % name)
        return self.__dict__[name]

    def _parse_data(self, data):
        info_str = data.splitlines()[0].replace('#', '', 1).strip()
        try:
            info_data = json.loads(info_str)
        except ValueError:
            info_data = {}
        return info_data

    def load(self):
        self.profile_name = None
        self.user_name = None
        self.org_name = None
        self.server_name = None

        with open(self.path, 'r') as profile_file:
            data = profile_file.read()
            info_data = self._parse_data(data)
            self.profile_name = info_data.get('name')
            self.user_name = info_data.get('user')
            self.org_name = info_data.get('organization')
            self.server_name = info_data.get('server')

    def write(self, data, default_name='Unknown Profile'):
        if not self._parse_data(data):
            data = '# {"name": "%s"}\n' % default_name + data
        with open(self.path, 'w') as profile_file:
            os.chmod(self.path, 0600)
            profile_file.write(data)

    def set_name(self, name):
        with open(self.path, 'r') as profile_file:
            data = profile_file.read()
            info_data = self._parse_data(data)
            if info_data:
                data = '\n'.join(data.splitlines()[1:])
            info_data['name'] = name
        data = '# %s\n' % json.dumps(info_data) + data
        self.write(data)

    def delete(self):
        os.remove(self.path)

    def _set_status(self, status):
        data = _connections.get(self.id)
        if not data:
            return
        data['status'] = status
        callback = data.get('dialog_callback')
        if callback:
            data['dialog_callback'] = None
            gobject.idle_add(callback)

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
