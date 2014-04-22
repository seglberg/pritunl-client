from constants import *
from exceptions import *
from profile import Profile, _connections
import time
import subprocess
import threading
import signal

_available_tap_adapters = 0

class ProfileWin(Profile):
    def _add_tap_adapter(self):
        devcon_path = os.path.join(WIN_TUNTAP_DIR, 'devcon.exe')
        subprocess.check_output([devcon_path, 'install',
            'OemWin2k.inf', 'tap0901'], cwd=WIN_TUNTAP_DIR,
            creationflags=0x08000000)

    def _start(self, status_callback, connect_callback, passwd):
        global _available_tap_adapters

        def on_exit(data, return_code):
            global _available_tap_adapters
            _available_tap_adapters += 1
            if self.status in ACTIVE_STATES:
                self._set_status(ERROR)

        if not _available_tap_adapters:
            self._add_tap_adapter()
        else:
            _available_tap_adapters -= 1

        args = [WIN_OPENVPN_PATH, '--config', self.path]

        if passwd:
            args.append('--auth-user-pass')
            args.append(self.passwd_path)

        self._run_ovpn(status_callback, connect_callback, passwd,
            args, on_exit, creationflags=0x08000000)

    def _start_autostart(self, status_callback, connect_callback):
        self._start(status_callback, connect_callback, None)

    def _stop(self, silent):
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
        if not silent:
            self._set_status(ENDED)
        self.pid = None
        self.commit()

    def _kill_pid(self, pid):
        for i in xrange(2):
            try:
                os.kill(pid, signal.SIGTERM)
            except OSError:
                pass

    @classmethod
    def _clear_tap_adapters(cls):
        devcon_path = os.path.join(WIN_TUNTAP_DIR, 'devcon.exe')
        subprocess.check_output([devcon_path, 'remove', 'tap0901'],
            cwd=WIN_TUNTAP_DIR, creationflags=0x08000000)

ProfileWin._clear_tap_adapters()
