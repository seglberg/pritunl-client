from pritunl_client.constants import *
from pritunl_client.exceptions import *

if PLATFORM == LINUX:
    from interface_gtk import *
else:
    raise TypeError('Interface not available for platform')
