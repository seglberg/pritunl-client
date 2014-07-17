import optparse
import sys
import pritunl_client.app

parser = optparse.OptionParser()
parser.add_option('--version', action='store_true', help='Print version')
(options, args) = parser.parse_args()

if options.version:
    print '%s v%s' % (pritunl.__title__, pritunl.__version__)
else:
    app = pritunl_client.app.App()
    app.main()
