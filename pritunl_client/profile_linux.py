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
        return os.path.join(os.path.abspath(os.sep),
            'etc', 'pritunl_client', self._get_profile_hash())

    def _start(self, status_callback, connect_callback, passwd, mode=START,
            retry=0):
        if self.autostart or mode == AUTOSTART:
            if not os.path.exists(self._get_profile_hash_path()):
                self.set_autostart(False)
                if mode == AUTOSTART:
                    return
            else:
                mode = AUTOSTART

        def on_exit(data, return_code):
            # Canceled
            if return_code == 126:
                self._set_status(ENDED)
            # Random error, retry
            elif return_code == -15 and not data['started'] and retry < 10:
                data['status_callback'] = None
                data['connect_callback'] = None
                time.sleep(0.1)
                self._start(status_callback, connect_callback, passwd, mode,
                    retry=retry)
            else:
                if self.status in ACTIVE_STATES:
                    self._set_status(ERROR)

        args = ['pkexec', '/usr/bin/pritunl_client_pk', mode, self.path]

        if passwd:
            args.append(self.passwd_path)

        self._run_ovpn(status_callback, connect_callback, passwd,
            args, on_exit)

    def _start_autostart(self, status_callback, connect_callback):
        self._start(status_callback, connect_callback, None, AUTOSTART)

    def _stop(self, silent, retry=0):
        retry += 1
        data = _connections.get(self.id)
        if data:
            process = data.get('process')
            data['process'] = None
            if process and not process.poll():
                stop_process = subprocess.Popen(['pkexec',
                    '/usr/bin/pritunl_client_pk', 'stop', str(process.pid)],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stop_process.wait()

                # Canceled
                if stop_process.returncode == 126:
                    return
                # Random error, retry
                elif stop_process.returncode == -15 and retry < 10:
                    time.sleep(0.1)
                    self._stop(silent=silent, retry=retry)
                    return
                elif stop_process.returncode != 0:
                    raise ProcessCallError(
                        'Pritunl polkit process returned error %s.' % (
                            stop_process.returncode))
        if not silent:
            self._set_status(ENDED)
        self.pid = None
        self.commit()

    def _set_profile_autostart(self, retry=0):
        retry += 1
        process = subprocess.Popen(['pkexec',
            '/usr/bin/pritunl_client_pk', 'set_autostart', self.path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.wait()

        # Canceled
        if process.returncode == 126:
            return False
        # Random error, retry
        elif process.returncode == -15 and retry < 10:
            time.sleep(0.1)
            return self._set_profile_autostart(retry=retry)
        elif process.returncode != 0:
            raise ProcessCallError(
                'Pritunl polkit process returned error %s.' % (
                    process.returncode))
        return True

    def _clear_profile_autostart(self, retry=0):
        retry += 1
        process = subprocess.Popen(['pkexec',
            '/usr/bin/pritunl_client_pk', 'clear_autostart',
            self._get_profile_hash()], stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        process.wait()

        # Canceled
        if process.returncode == 126:
            return False
        # Random error, retry
        elif process.returncode == -15 and retry < 10:
            time.sleep(0.1)
            return self._clear_profile_autostart(retry=retry)
        elif process.returncode != 0:
            raise ProcessCallError(
                'Pritunl polkit process returned error %s.' % (
                    process.returncode))
        return True

    def _kill_pid(self, pid, retry=0):
        retry += 1
        process = subprocess.Popen(['pkexec',
            '/usr/bin/pritunl_client_pk', 'stop', str(pid)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.wait()

        # Random error, retry
        if process.returncode == -15 and retry < 10:
            time.sleep(0.1)
            self._kill_pid(pid, retry=retry)

    def commit(self):
        if os.path.exists(self._get_profile_hash_path()) != self.autostart:
            if self.autostart:
                if not self._set_profile_autostart():
                    return
            else:
                if not self._clear_profile_autostart():
                    return
        Profile.commit(self)

    def delete(self):
        if os.path.exists(self._get_profile_hash_path()):
            if not self._clear_profile_autostart():
                return
        Profile.delete(self)
