from constants import *
import gtk

def get_logo():
    if PLATFORM == LINUX:
        icons = gtk.icon_theme_get_default()
        logo = icons.lookup_icon('pritunl_client', -1, 0)
        if logo:
            return logo.get_filename()
    return LOGO_DEFAULT_PATH

def get_connected_logo():
    if PLATFORM == LINUX:
        icons = gtk.icon_theme_get_default()
        logo = icons.lookup_icon('pritunl_client_connected', -1, 0)
        if logo:
            return logo.get_filename()
    return CONNECTED_LOGO_DEFAULT_PATH

def get_disconnected_logo():
    if PLATFORM == LINUX:
        icons = gtk.icon_theme_get_default()
        logo = icons.lookup_icon('pritunl_client_disconnected', -1, 0)
        if logo:
            return logo.get_filename()
    return DISCONNECTED_LOGO_DEFAULT_PATH
