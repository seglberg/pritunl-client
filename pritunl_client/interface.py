from pritunl_client.constants import *
from pritunl_client.exceptions import *

if PLATFORM == LINUX:
    from interface_gtk import *
elif PLATFORM in (WIN, OSX):
    from interface_wx import *
