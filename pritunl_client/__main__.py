import optparse
import sys
import os
import re
import subprocess
import signal
import time

def client():
    import pritunl_client.interface
    parser = optparse.OptionParser()
    parser.add_option('--version', action='store_true', help='Print version')
    (options, args) = parser.parse_args()

    if options.version:
        print '%s v%s' % (pritunl.__title__, pritunl.__version__)
        sys.exit(0)

    interface = pritunl_client.interface.Interface()
    interface.main()

def pk():
    if sys.argv[1] in ('start', 'autostart'):
        regex_etc = r'^/etc/pritunl_client/[a-z0-9]+.ovpn$'
        regex_home = r'(?:/pritunl_client/profiles/[a-z0-9]+\.ovpn)$'
        if sys.argv[1] == 'autostart' and not re.match(regex_etc, sys.argv[2]):
            raise ValueError('Autostart profile must be in etc directory')
        if sys.argv[1] == 'start' and not re.search(regex_home, sys.argv[2]):
            raise ValueError('Profile must be in home directory')
        process = subprocess.Popen(['openvpn', sys.argv[2]])
        def sig_handler(signum, frame):
            process.send_signal(signum)
        signal.signal(signal.SIGINT, sig_handler)
        signal.signal(signal.SIGTERM, sig_handler)
        sys.exit(process.wait())
    elif sys.argv[1] == 'stop':
        regex_etc = r'(?:/etc/pritunl_client/[a-z0-9]+.ovpn)$'
        regex_home = r'(?:/pritunl_client/profiles/[a-z0-9]+\.ovpn)$'
        with open('/proc/%s/cmdline' % int(sys.argv[2]), 'r') as cmdline_file:
            cmdline = cmdline_file.read().strip().strip('\x00')
            if not re.search(regex_etc, cmdline) and \
                    not re.search(regex_home, cmdline):
                raise ValueError('Not a pritunl client process')
        os.kill(int(sys.argv[2]), os.SIGTERM)
        for i in xrange(int(5 / 0.1)):
            time.sleep(0.1)
            if not os.path.exists('/proc/%s' % int(sys.argv[2])):
                break
            os.kill(int(sys.argv[2]), os.SIGTERM)
    elif sys.argv[1] == 'copy':
        regex = r'(?:/pritunl_client/profiles/[a-z0-9]+\.ovpn)$'
        if not re.search(regex, sys.argv[2]):
            raise ValueError('Profile must be in home directory')
        subprocess.check_call(['cp', '--preserve=mode', sys.argv[2],
            os.path.join(os.path.abspath(os.sep), 'etc', 'pritunl_client')])
    elif sys.argv[1] == 'remove':
        regex = r'^/etc/pritunl_client/[a-z0-9]+.ovpn$'
        if not re.match(regex, sys.argv[2]):
            raise ValueError('Profile must be in etc directory')
        subprocess.check_call(['rm', sys.argv[2]])
