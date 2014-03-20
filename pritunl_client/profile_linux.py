from constants import *
from exceptions import *
from profile import Profile, _connections
import os
import time
import subprocess
import threading

class ProfileLinux(Profile):
    def _start(self, status_callback, dialog_callback):
        data = {
            'status': CONNECTING,
            'process': None,
            'status_callback': status_callback,
            'dialog_callback': dialog_callback,
        }
        _connections[self.id] = data

        process = subprocess.Popen([
            'pkexec', '/usr/sbin/openvpn', self.path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        data['process'] = process

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
                    self._set_status(CONNECTED)
                elif 'Inactivity timeout' in line:
                    self._set_status(RECONNECTING)
            # Canceled
            if process.returncode == 126:
                self._set_status(ENDED)
            else:
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

    def _stop(self):
        data = _connections.get(self.id)
        if data:
            process = data.get('process')
            if process:
                stop_cmd = ['pkexec', '/usr/bin/pritunl_client_pk',
                    'stop', str(process.pid)]
                subprocess.check_call(stop_cmd)
                for i in xrange(int(5 / 0.1)):
                    time.sleep(0.1)
                    if process.poll() is not None:
                        return
                    subprocess.check_call(stop_cmd)

        self._set_status(ENDED)
