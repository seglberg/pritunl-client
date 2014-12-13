import os
os.environ['LINUX_SHELL'] = 't'

from pritunl_client import __main__
__main__.shell()

