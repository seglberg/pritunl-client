from constants import *
import os
import uuid
import json
import time
import subprocess
import threading
import signal
import gtk
import gobject

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
        process = subprocess.Popen(['gksudo', '--description',
            'Pritunl Connect', 'openvpn %s' % self.path],
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
                if not line:
                    if process.poll() is not None:
                        break
                    else:
                        continue
                print line.strip()
                if 'Initialization Sequence Completed' in line:
                    change_status(True)
                elif 'Inactivity timeout' in line:
                    change_status(False)
            print 'EXIT_OVPN'
            data.pop(self.id, None)
            change_status(False)

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
        if not connection_data:
            return

        process = connection_data.get('process')
        if not process:
            return

        # TODO run in thread
        for i in xrange(10):
            kill_process = subprocess.Popen(['gksudo', '--description',
                'Pritunl Disconnect', 'pkill -P %s' % process.pid],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            pass_fail = False

            while True:
                line = kill_process.stderr.readline()
                if not line:
                    if kill_process.poll() is not None:
                        break
                    else:
                        continue
                if 'incorrect password' in line:
                    pass_fail = True

            if kill_process.poll() == 255:
                return

            if pass_fail:
                dialog = gtk.MessageDialog(
                    type=gtk.MESSAGE_ERROR,
                    buttons=gtk.BUTTONS_OK,
                    message_format='Password is incorrect, try again...')
                dialog.format_secondary_markup(
                    'Failed to obtain sudo privileges')
                dialog.set_title('Pritunl - Incorrect Password')
                dialog.show_all()
                dialog.run()
                dialog.destroy()
                continue

            for i in xrange(int(OVPN_EXIT_TIMEOUT / 0.1)):
                time.sleep(0.1)
                if process.poll() is not None:
                    break

            break

        if process.poll() is None:
            dialog = gtk.MessageDialog(
                type=gtk.MESSAGE_ERROR,
                buttons=gtk.BUTTONS_OK,
                message_format='Unable to disconnect profile')
            dialog.format_secondary_markup(
                'Failed to stop profile connection process')
            dialog.set_title('Pritunl - Disconnect Failed')
            dialog.show_all()
            dialog.run()
            dialog.destroy()


        # for i in xrange(int(OVPN_EXIT_TIMEOUT / 0.1)):
        #     time.sleep(0.1)
        #     if process.poll() is not None:
        #         break
        #     process.terminate()
        # if process.poll() is not None:
        #     return

        # process.kill()
        # for i in xrange(int(OVPN_EXIT_TIMEOUT / 0.1)):
        #     time.sleep(0.1)
        #     if process.poll() is not None:
        #         break
        #     process.kill()

    @classmethod
    def iter_profiles(cls):
        if os.path.isdir(PROFILES_DIR):
            for profile_id in os.listdir(PROFILES_DIR):
                profile_id = profile_id.replace('.ovpn', '')
                yield Profile(profile_id)
