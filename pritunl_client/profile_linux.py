from constants import *
from exceptions import *
from profile import Profile, _connections
import os
import time
import subprocess
import threading

class ProfileLinux(Profile):
    def _start(self, status_callback, dialog_callback, retry=True):
        data = {
            'status': CONNECTING,
            'process': None,
            'status_callback': status_callback,
            'dialog_callback': dialog_callback,
        }
        _connections[self.id] = data

        process = subprocess.Popen([
            'pkexec', '/usr/bin/pritunl_client_pk', 'start', self.path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        data['process'] = process

        def dialog_thread():
            time.sleep(CONNECT_TIMEOUT)
            if not data.get('dialog_callback'):
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
                    thread = threading.Thread(target=dialog_thread)
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
                data['dialog_callback'] = None
                self._start(status_callback, dialog_callback, False)
            else:
                self._set_status(DISCONNECTED)

        thread = threading.Thread(target=poll_thread)
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
