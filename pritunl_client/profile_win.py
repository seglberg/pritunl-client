from constants import *
from exceptions import *
from profile import Profile, _connections
import time
import subprocess
import threading

class ProfileWin(Profile):
    def _start(self, status_callback, connect_callback):
        data = {
            'status': CONNECTING,
            'process': None,
            'status_callback': status_callback,
            'connect_callback': connect_callback,
        }
        _connections[self.id] = data
        self._set_status(CONNECTING, connect_event=False)

        process = subprocess.Popen(['openvpn.exe', self.path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        data['process'] = process

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
                # TODO
                print line.strip()
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
            self._set_status(DISCONNECTED)

        thread = threading.Thread(target=poll_thread)
        thread.daemon = True
        thread.start()

    def _start_autostart(self, status_callback, connect_callback):
        self._start(status_callback, connect_callback)

    def _stop(self):
        data = _connections.get(self.id)
        if data:
            process = data.get('process')
            data['process'] = None
            if process:
                process.terminate()
                for i in xrange(int(5 / 0.1)):
                    time.sleep(0.1)
                    if process.poll() is not None:
                        return
                    process.terminate()

                process.kill()
                for i in xrange(int(5 / 0.1)):
                    time.sleep(0.1)
                    if process.poll() is not None:
                        return
                    process.kill()
        self._set_status(ENDED)
