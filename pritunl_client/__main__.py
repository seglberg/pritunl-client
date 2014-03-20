from constants import *
import optparse
import sys
import os
import re
import subprocess

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
    if sys.argv[1] == 'stop':
        regex = r'(?:/pritunl/profiles/[a-z0-9]+\.ovpn)$'
        with open('/proc/%s/cmdline' % sys.argv[2], 'r') as cmdline_file:
            cmdline = cmdline_file.read().strip('\x00')
            if not re.search(regex, cmdline):
                raise ValueError('Not a pritunl client process')
        subprocess.check_call(['kill', sys.argv[2]])
    elif sys.argv[1] == 'copy':
        pass
