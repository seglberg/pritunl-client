from constants import *
from exceptions import *
from profile import Profile, _connections
import os
import time
import subprocess
import threading
import hashlib

class ProfileLinux(Profile):
    def __init__(self, *args, **kwargs):
        Profile.__init__(self, *args, **kwargs)

    def _get_profile_hash(self):
        with open(self.path, 'r') as profile_file:
            return hashlib.sha1(profile_file.read()).hexdigest()

    def _get_profile_hash_path(self):
        profile_hash = self._get_profile_hash()
        return os.path.join(os.path.abspath(os.sep),
            'etc', 'pritunl_client', profile_hash)

    def _start(self, status_callback, connect_callback, mode=START,
            retry=True):
        if mode == AUTOSTART:
            if not os.path.exists(self._get_profile_hash_path()):
                self.set_autostart(False)
                return
        else:
            path = self.path

        data = {
            'status': CONNECTING,
            'process': None,
            'status_callback': status_callback,
            'connect_callback': connect_callback,
        }
        _connections[self.id] = data

        process = subprocess.Popen([
            'pkexec', '/usr/bin/pritunl_client_pk', mode, self.path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        data['process'] = process

        def connect_thread():
            time.sleep(CONNECT_TIMEOUT)
            if not data.get('connect_callback'):
                return
            self.stop()

        def poll_thread():
            started = False
            while True:
                line = process.stdout.readline()
                if not line:
                    if process.poll() is not None:
                        break
                    else:
                        continue
                # TODO log
                print line.strip()
                if not started:
                    started = True
                    thread = threading.Thread(target=connect_thread)
                    thread.daemon = True
                    thread.start()
                if 'Initialization Sequence Completed' in line:
                    self._set_status(CONNECTED)
                elif 'Inactivity timeout' in line:
                    self._set_status(RECONNECTING)

            # Canceled
            if process.returncode == 126:
                self._set_status(ENDED)
            # Random error, retry
            elif process.returncode == -15 and not started and retry:
                data['status_callback'] = None
                data['connect_callback'] = None
                self._start(status_callback, connect_callback, mode,
                    retry=False)
                return
            else:
                self._set_status(DISCONNECTED)

        thread = threading.Thread(target=poll_thread)
        thread.daemon = True
        thread.start()

    def _start_autostart(self, status_callback, connect_callback):
        self._start(status_callback, connect_callback, AUTOSTART)

    def _stop(self, retry=True):
        data = _connections.get(self.id)
        if data:
            process = data.get('process')
            if process and not process.poll():
                stop_process = subprocess.Popen(['pkexec',
                    '/usr/bin/pritunl_client_pk', 'stop', str(process.pid)],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stop_process.wait()

                # Canceled
                if stop_process.returncode == 126:
                    return
                # Random error, retry
                elif stop_process.returncode == -15 and retry:
                    self._stop(retry=False)
                    return
                elif stop_process.returncode != 0:
                    raise ProcessCallError(
                        'Pritunl polkit process returned error %s.' % (
                            stop_process.returncode))
            data['process'] = None
        self._set_status(ENDED)

    def _set_profile_autostart(self, retry=True):
        process = subprocess.Popen(['pkexec',
            '/usr/bin/pritunl_client_pk', 'set_autostart', self.path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.wait()

        # Canceled
        if process.returncode == 126:
            return
        # Random error, retry
        elif process.returncode == -15 and retry:
            self._copy_profile_autostart(retry=False)
            return
        elif process.returncode != 0:
            raise ProcessCallError(
                'Pritunl polkit process returned error %s.' % (
                    process.returncode))

    def _clear_profile_autostart(self, retry=True):
        process = subprocess.Popen(['pkexec',
            '/usr/bin/pritunl_client_pk', 'clear_autostart',
            self._get_profile_hash()], stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        process.wait()

        # Canceled
        if process.returncode == 126:
            return
        # Random error, retry
        elif process.returncode == -15 and retry:
            self._remove_profile_autostart(retry=False)
            return
        elif process.returncode != 0:
            raise ProcessCallError(
                'Pritunl polkit process returned error %s.' % (
                    process.returncode))

    def commit(self):
        Profile.commit(self)
        if os.path.exists(self._get_profile_hash_path()) != self.autostart:
            if self.autostart:
                self._set_profile_autostart()
            else:
                self._clear_profile_autostart()

    def delete(self):
        if os.path.exists(self._get_profile_hash_path()):
            self._clear_profile_autostart()
        Profile.delete(self)
