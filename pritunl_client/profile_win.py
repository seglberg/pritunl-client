from constants import *
from exceptions import *
from profile import Profile, _connections
import time
import subprocess
import threading
import signal

class ProfileWin(Profile):
    def _start(self, status_callback, connect_callback, passwd):
        def on_exit(returncode):
            if self.state in ACTIVE_STATES:
                self._set_status(ERROR)

        args = ['openvpn.exe', '--config', self.path]

        if passwd:
            with open(self.passwd_path, 'w') as passwd_file:
                os.chmod(self.passwd_path, 0600)
                passwd_file.write('pritunl_client\n')
                passwd_file.write('%s\n' % passwd)
            args.append('--auth-user-pass')
            args.append(self.passwd_path)

        self._run_ovpn(status_callback, connect_callback, passwd,
            args, on_exit)

    def _start_autostart(self, status_callback, connect_callback):
        self._start(status_callback, connect_callback, None)

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
        if self.state in ACTIVE_STATES:
            self._set_status(ENDED)
        self.pid = None
        self.commit()

    def _kill_pid(self, pid):
        for i in xrange(2):
            try:
                os.kill(pid, signal.SIGTERM)
            except OSError:
                pass
