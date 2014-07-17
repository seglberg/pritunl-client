import pritunl_client.profile_win
import sys
import ctypes
import win32con
import win32event
import win32process
from win32com.shell import shell
from win32com.shell import shellcon

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
    sys.exit(0)

pritunl_client.profile_win.ProfileWin.clear_tap_adapters()
