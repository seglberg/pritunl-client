from constants import *

if PLATFORM == LINUX:
    from interface_gtk import *
elif PLATFORM in (WIN, OSX):
    from interface_wx import *
