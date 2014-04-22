import optparse
import sys
import os
import pritunl_client.app
import ctypes
import win32con
import win32event
import win32process
from win32com.shell import shell
from win32com.shell import shellcon

parser = optparse.OptionParser()
parser.add_option('--version', action='store_true', help='Print version')
(options, args) = parser.parse_args()

if options.version:
    print '%s v%s' % (pritunl.__title__, pritunl.__version__)
    sys.exit(0)

try:
    is_admin = ctypes.windll.shell32.IsUserAnAdmin()
except:
    is_admin = False

if not is_admin:
    cmd = '"%s"' % sys.executable
    params = ' '.join(['"%s"' % x for x in sys.argv])

    proc_info = shell.ShellExecuteEx(nShow=win32con.SW_SHOWNORMAL,
        fMask=shellcon.SEE_MASK_NOCLOSEPROCESS,
        lpVerb='runas', lpFile=cmd, lpParameters=params)

    proc_handle = proc_info['hProcess']
    obj = win32event.WaitForSingleObject(proc_handle, win32event.INFINITE)
    rc = win32process.GetExitCodeProcess(proc_handle)
else:
    app = pritunl_client.app.App()
    app.main()
