from constants import *
from exceptions import *
from profile import Profile, _connections
from daemon_client import DaemonClient
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
        log_path = os.path.join(TMP_DIR, 'pritunl_%s.log' % self.id)

        client = DaemonClient()
        try:
            client.start_conn(self.id, self.working_dir, self.path, log_path)
        except SudoPassFail:
            self._set_status(ENDED, SUDO_PASS_FAIL)
            return
        except SudoCancel:
            self._set_status(ENDED)
            return

        for i in xrange(int(OVPN_START_TIMEOUT / 0.1)):
            time.sleep(0.1)
            if os.path.exists(log_path):
                break
        if not os.path.exists(log_path):
            self.stop()

        def poll_thread():
            process = subprocess.Popen(['tail', '-c', '+1',
                '--follow=name', log_path], stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            data['process'] = process
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
        client = DaemonClient()
        client.stop_conn(self.id)

        data = _connections.get(self.id)
        if data:
            process = data.get('process')
            if process:
                process.kill()

        self._set_status(ENDED)
