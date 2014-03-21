from constants import *
from exceptions import *
from profile import Profile, _connections
import os
import time
import subprocess
import threading

class ProfileLinux(Profile):
    def __init__(self, *args, **kwargs):
        Profile.__init__(self, *args, **kwargs)
        self.autostart_path = os.path.join(LINUX_ETC_DIR, '%s.ovpn' % self.id)

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

    def _copy_profile_autostart(self):
        # TODO remove conf_str from autostart conf
        subprocess.check_call([
            'pkexec', '/usr/bin/pritunl_client_pk', 'copy', self.path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def _remove_profile_autostart(self):
        subprocess.check_call(['pkexec',
            '/usr/bin/pritunl_client_pk', 'remove', self.autostart_path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def write(self, data, *args, **kwargs):
        Profile.write(self, data, *args, **kwargs)
        conf_data = self._parse_conf(data)
        if os.path.exists(self.autostart_path) != conf_data.get('autostart'):
            if conf_data.get('autostart'):
                self._copy_profile_autostart()
            else:
                self._remove_profile_autostart()
