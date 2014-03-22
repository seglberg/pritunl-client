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
        self.autostart = False

        if not os.path.isdir(PROFILES_DIR):
            os.makedirs(PROFILES_DIR)

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

    def _parse_conf(self, data):
        conf_str = data.splitlines()[0].replace('#', '', 1).strip()
        try:
            conf_data = json.loads(conf_str)
        except ValueError:
            conf_data = {}
        return conf_data

    def load(self):
        with open(self.path, 'r') as profile_file:
            data = profile_file.read()
            conf_data = self._parse_conf(data)
            self.profile_name = conf_data.get('name')
            self.user_name = conf_data.get('user')
            self.org_name = conf_data.get('organization')
            self.server_name = conf_data.get('server')
            self.autostart = conf_data.get('autostart') or False

    def write(self, data, default_name='Unknown Profile'):
        conf_data = self._parse_conf(data)
        if not conf_data:
            data = '# {"name": "%s"}\n' % default_name + data
        with open(self.path, 'w') as profile_file:
            os.chmod(self.path, 0600)
            profile_file.write(data)

    def _set_conf(self, name, value):
        with open(self.path, 'r') as profile_file:
            data = profile_file.read()
            conf_data = self._parse_conf(data)
            if conf_data:
                data = '\n'.join(data.splitlines()[1:])
            conf_data[name] = value
        data = '# %s\n' % json.dumps(conf_data) + data
        self.write(data)

    def set_name(self, name):
        self._set_conf('name', name)

    def set_autostart(self, state):
        self._set_conf('autostart', state)

    def delete(self):
        os.remove(self.path)

    def _set_status(self, status):
        data = _connections.get(self.id)
        if not data:
            return
        data['status'] = status
        callback = data.get('connect_callback')
        if callback:
            data['connect_callback'] = None
            gobject.idle_add(callback)

        callback = data.get('status_callback')
        if callback:
            gobject.idle_add(callback)

    def start(self, status_callback, connect_callback=None):
        if self.status not in (DISCONNECTED, ENDED):
            self._set_status(self.status)
            return
        self._start(status_callback, connect_callback)

    def start_autostart(self, status_callback, connect_callback=None):
        if self.status not in (DISCONNECTED, ENDED):
            return
        self._start_autostart(status_callback, connect_callback)

    def _start(self, status_callback, connect_callback=None):
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
