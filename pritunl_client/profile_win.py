from constants import *
from exceptions import *
from profile import Profile, _connections
import time
import subprocess
import threading
import signal

tap_adapters = {
    'in_use': 0,
    'available': 0,
}

class ProfileWin(Profile):
    def _start(self, status_callback, connect_callback, passwd):
        try:
            ipconfig = subprocess.check_output(['ipconfig', '/all'])
            tap_adapters['in_use'] = 0
            tap_adapters['available'] = 0
            tap_adapter = False
            tap_disconnected = False
            for line in ipconfig.split('\n'):
                line = line.strip()
                if line == '':
                    if tap_adapter:
                        tap_adapters['available'] += 1
                        if not disconnected:
                            tap_adapters['in_use'] += 1
                    tap_adapter = False
                    disconnected = False
                elif 'TAP-Windows Adapter V9' in line:
                    tap_adapter = True
                elif 'Media disconnected' in line:
                    disconnected = True
        except (WindowsError, subprocess.CalledProcessError):
            pass

        def on_exit(data, return_code):
            tap_adapters['in_use'] -= 1
            if self.status in ACTIVE_STATES:
                self._set_status(ERROR)

        if not tap_adapters['available'] - tap_adapters['in_use']:
            self.add_tap_adapter()
        tap_adapters['in_use'] += 1

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
                        break
                    process.terminate()

                for i in xrange(int(5 / 0.1)):
                    time.sleep(0.1)
                    if process.poll() is not None:
                        break
                    process.kill()
                self._reset_networking()
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
    def _reset_networking(cls):
        for command in (
                    ['route', '-f'],
                    ['ipconfig', '/release'],
                    ['ipconfig', '/renew'],
                    ['arp', '-d', '*'],
                    ['nbtstat', '-R'],
                    ['nbtstat', '-RR'],
                    ['ipconfig', '/flushdns'],
                    ['nbtstat', '/registerdns'],
                ):
            try:
                subprocess.check_output(command, creationflags=0x08000000)
            except:
                pass

    @classmethod
    def add_tap_adapter(cls):
        devcon_path = os.path.join(WIN_TUNTAP_DIR, 'devcon.exe')
        subprocess.check_output([devcon_path, 'install',
            'OemWin2k.inf', 'tap0901'], cwd=WIN_TUNTAP_DIR,
            creationflags=0x08000000)

    @classmethod
    def clear_tap_adapters(cls):
        devcon_path = os.path.join(WIN_TUNTAP_DIR, 'devcon.exe')
        subprocess.check_output([devcon_path, 'remove', 'tap0901'],
            cwd=WIN_TUNTAP_DIR, creationflags=0x08000000)
        cls._reset_networking()
