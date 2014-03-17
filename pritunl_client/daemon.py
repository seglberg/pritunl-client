import socket
import os
import threading
import json
import subprocess
import time
import sys

class Daemon:
    def __init__(self):
        self._procs = {}

    def start_conn(self, id, working_dir, path, log_path):
        def target():
            if os.path.exists(log_path):
                os.remove(log_path)
            with open(log_path, 'w') as log_file:
                pass
            process = subprocess.Popen(['openvpn', '--log-append',
                log_path, '--config', path], cwd=working_dir)
            self._procs[id] = process
            return_code = process.wait()
            if os.path.exists(log_path):
                os.remove(log_path)
            self._procs.pop(id, None)
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()

    def stop_conn(self, id):
        process = self._procs.get(id)
        if not process:
            return

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

    def run(self):
        sock_path = sys.argv[1]

        if os.path.exists(sock_path):
            os.remove(sock_path)

        try:
            server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            server.bind(sock_path)
            server.listen(5)
            os.chmod(sock_path, 0777)

            while True:
                conn, addr = server.accept()
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    data = json.loads(data)
                    if data['cmd'] == 'start':
                        self.start_conn(data['id'], data['working_dir'],
                            data['path'], data['log_path'])
                    elif data['cmd'] == 'stop':
                        self.stop_conn(data['id'])
                    elif data['cmd'] == 'exit':
                        return
            server.close()
        finally:
            if os.path.exists(sock_path):
                os.remove(sock_path)
            for conn_id in self._procs.keys():
                process = self._procs.pop(conn_id, None)
                if not process:
                    continue
                try:
                    process.kill()
                except:
                    pass
