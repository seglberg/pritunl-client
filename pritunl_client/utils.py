from constants import *
import interface

def get_logo():
    if PLATFORM == LINUX:
        logo_path = interface.lookup_icon('pritunl_client')
        if logo_path:
            return logo_path
    return LOGO_DEFAULT_PATH

def get_connected_logo():
    if PLATFORM == LINUX:
        logo_path = interface.lookup_icon('pritunl_client_connected')
        if logo_path:
            return logo_path
    return CONNECTED_LOGO_DEFAULT_PATH

def get_disconnected_logo():
    if PLATFORM == LINUX:
        logo_path = interface.lookup_icon('pritunl_client_disconnected')
        if logo_path:
            return logo_path
    return DISCONNECTED_LOGO_DEFAULT_PATH
