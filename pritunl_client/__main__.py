import optparse
import sys
import os
import re
import subprocess
import signal

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
        regex = r'^/etc/pritunl_client/[a-z0-9]+.ovpn$'
        if sys.argv[1] == 'autostart' and not re.match(regex, sys.argv[2]):
            raise ValueError('Autostart profile must be in etc directory')
        process = subprocess.Popen(['openvpn', sys.argv[2]])
        def sig_handler(signum, frame):
            process.send_signal(signum)
        signal.signal(signal.SIGINT, sig_handler)
        signal.signal(signal.SIGTERM, sig_handler)
        sys.exit(process.wait())
    elif sys.argv[1] == 'stop':
        regex = r'(?:/pritunl/profiles/[a-z0-9]+\.ovpn)$'
        with open('/proc/%s/cmdline' % sys.argv[2], 'r') as cmdline_file:
            cmdline = cmdline_file.read().strip().strip('\x00')
            if not re.search(regex, cmdline):
                raise ValueError('Not a pritunl client process')
        subprocess.check_call(['kill', sys.argv[2]])
    elif sys.argv[1] == 'copy':
        subprocess.check_call(['cp', '--preserve=mode', sys.argv[2],
            os.path.join(os.path.abspath(os.sep), 'etc', 'pritunl_client')])
    elif sys.argv[1] == 'remove':
        regex = r'^/etc/pritunl_client/[a-z0-9]+.ovpn$'
        if not re.match(regex, sys.argv[2]):
            raise ValueError('Profile must be in etc directory')
        subprocess.check_call(['rm', sys.argv[2]])
