from constants import *
from exceptions import *
import socket
import sys
import json
import subprocess
import time
import threading
import gtk
import gobject

_data = {
    'process': None,
    'sock': None,
}

class DaemonClient:
    def open(self):
        process = subprocess.Popen(['gksudo', '--description',
            'Pritunl Client', 'python2 daemon.py %s' % SOCK_PATH],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _data['process'] = process
        thread_data = {
            'pass_fail': False,
        }

        def target():
            while True:
                line = process.stderr.readline()
                if not line:
                    if process.poll() is not None:
                        break
                    else:
                        continue
                if 'incorrect password' in line:
                    thread_data['pass_fail'] = True

        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()

        while True:
            if os.path.exists(SOCK_PATH):
                break
            elif process.poll() is not None:
                break
            time.sleep(0.1)

        if process.poll() == 255:
            raise SudoCancel()

        if thread_data['pass_fail']:
            raise SudoPassFail()

        if process.poll() is not None:
            # TODO possible pass fail msg not printed or daemon error
            raise SudoPassFail()

        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(SOCK_PATH)
        _data['sock'] = sock

    def close(self):
        sock = _data.get('sock')
        if not sock:
            sock.close()

    def send(self, data):
        sock = _data.get('sock')
        if not sock:
            self.open()
        sock = _data.get('sock')
        if not sock:
            return
        sock.sendall(json.dumps(data))

    def start_conn(self, id, working_dir, path, log_path):
        self.send({
            'cmd': 'start',
            'id': id,
            'working_dir': working_dir,
            'path': path,
            'log_path': log_path,
        })

    def stop_conn(self, id):
        self.send({
            'cmd': 'stop',
            'id': id,
        })

    def exit(self):
        if not _data.get('sock'):
            return
        self.send({
            'cmd': 'exit',
        })
