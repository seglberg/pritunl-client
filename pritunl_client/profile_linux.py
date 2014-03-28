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

    def _start(self, status_callback, connect_callback, passwd, mode=START,
            retry=0):
        if self.autostart or mode == AUTOSTART:
            if not os.path.exists(self._get_profile_hash_path()):
                self.set_autostart(False)
                if mode == AUTOSTART:
                    return
            else:
                mode = AUTOSTART

        data = {
            'status': CONNECTING,
            'process': None,
            'status_callback': status_callback,
            'connect_callback': connect_callback,
            'passwd_path': None,
        }
        _connections[self.id] = data
        retry += 1
        self._set_status(CONNECTING, connect_event=False)

        args = ['pkexec', '/usr/bin/pritunl_client_pk', mode, self.path]

        if passwd:
            with open(self.passwd_path, 'w') as passwd_file:
                os.chmod(self.passwd_path, 0600)
                passwd_file.write('pritunl_client\n')
                passwd_file.write('%s\n' % passwd)
            args.append(self.passwd_path)

        process = subprocess.Popen(args,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        data['process'] = process
        self.pid = process.pid
        self.commit()

        def connect_thread():
            time.sleep(CONNECT_TIMEOUT)
            if not data.get('connect_callback'):
                return
            self.stop()

        def poll_thread():
            started = False
            with open(self.log_path, 'w') as log_file:
                pass
            while True:
                line = process.stdout.readline()
                if not line:
                    if process.poll() is not None:
                        break
                    else:
                        continue
                with open(self.log_path, 'a') as log_file:
                    log_file.write(line)
                if not started:
                    started = True
                    thread = threading.Thread(target=connect_thread)
                    thread.daemon = True
                    thread.start()
                if 'Initialization Sequence Completed' in line:
                    self._set_status(CONNECTED)
                elif 'Inactivity timeout' in line:
                    self._set_status(RECONNECTING)

            if passwd:
                try:
                    os.remove(self.passwd_path)
                except:
                    pass

            # Canceled
            if process.returncode == 126:
                self._set_status(ENDED)
            # Random error, retry
            elif process.returncode == -15 and not started and retry < 6:
                time.sleep(0.1)
                data['status_callback'] = None
                data['connect_callback'] = None
                self._start(status_callback, connect_callback, passwd, mode,
                    retry=retry)
                return
            else:
                self._set_status(DISCONNECTED)

        thread = threading.Thread(target=poll_thread)
        thread.daemon = True
        thread.start()

    def _start_autostart(self, status_callback, connect_callback):
        self._start(status_callback, connect_callback, None, AUTOSTART)

    def _stop(self, retry=0):
        retry += 1
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
                elif stop_process.returncode == -15 and retry < 6:
                    time.sleep(0.1)
                    self._stop(retry=retry)
                    return
                elif stop_process.returncode != 0:
                    raise ProcessCallError(
                        'Pritunl polkit process returned error %s.' % (
                            stop_process.returncode))
            data['process'] = None
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
        elif process.returncode == -15 and retry < 6:
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
        elif process.returncode == -15 and retry < 6:
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
        if process.returncode == -15 and retry < 6:
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
