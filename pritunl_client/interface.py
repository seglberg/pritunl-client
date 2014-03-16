from constants import *
from profile import Profile
import pygtk
pygtk.require('2.0')
import gtk

gtk.gdk.threads_init()

class Interface:
    def __init__(self):
        self.icon = gtk.StatusIcon()
        self.icon_state = None
        self.set_icon_state(False)
        self.icon.connect('activate', self.on_click_left)
        self.icon.connect('popup_menu', self.on_click_right)
        self.icon.set_tooltip_text('Connections: 0 active')

    def set_icon_state(self, state):
        if state == self.icon_state:
            return

        self.icon_state = state
        if state:
            self.icon.set_from_file('img/connected.svg')
        else:
            self.icon.set_from_file('img/disconnected.svg')

    def get_icon_state(self):
        return self.icon_state

    def on_click_left(self, widget):
        self.show_menu(0, 0)

    def on_click_right(self, widget, button, activate_time):
        self.show_menu(button, gtk.gdk.CURRENT_TIME)

    def show_connect_success(self, profile):
        dialog = gtk.MessageDialog(
            type=gtk.MESSAGE_INFO,
            buttons=gtk.BUTTONS_OK,
            message_format='Connected to %s' % profile.server_name)
        dialog.format_secondary_markup('Successfully connected to the server')
        dialog.set_title('Pritunl - Connection Successful')
        dialog.show_all()

        dialog.run()
        dialog.destroy()

    def show_connect_error(self, profile):
        dialog = gtk.MessageDialog(
            type=gtk.MESSAGE_ERROR,
            buttons=gtk.BUTTONS_OK,
            message_format='Unable to connect to %s' % profile.server_name)
        dialog.format_secondary_markup(
            'An error occurred while connecting to server')
        dialog.set_title('Pritunl - Connection Error')
        dialog.show_all()

        dialog.run()
        dialog.destroy()

    def on_status_change(self, profile):
        conn_count = 0

        for profile in Profile.iter_profiles():
            if profile.status:
                conn_count += 1

        self.icon.set_tooltip_text('Connections: %s active' % conn_count)
        self.set_icon_state(bool(conn_count))

    def on_toggle_profile(self, widget, profile):
        # widget.get_active()

        dialog = gtk.MessageDialog(
            type=gtk.MESSAGE_QUESTION,
            buttons=gtk.BUTTONS_CANCEL,
            message_format='Connecting to %s' % profile.server_name)
        dialog.format_secondary_markup('Conecting to the server...')
        dialog.set_title('Pritunl - Connecting...')

        spinner = gtk.Spinner()
        spinner.set_size_request(45, 45)
        spinner.start()
        dialog.set_image(spinner)
        dialog.show_all()

        def dialog_callback(profile):
            dialog.destroy()
        profile.start(self.on_status_change, dialog_callback)

        response = dialog.run()
        dialog.destroy()

        if profile.status:
            self.show_connect_success(profile)
        else:
            self.show_connect_error(profile)

    def on_disconnect_all(self, widget):
        pass

    def show_menu(self, event_button, activate_time):
        menu = gtk.Menu()
        profiles_menu = gtk.Menu()
        conn_active = True

        menu_item = gtk.MenuItem('Toggle Profile Connections')
        menu_item.set_sensitive(False)
        profiles_menu.append(menu_item)
        menu_item.show()

        menu_item = gtk.SeparatorMenuItem()
        profiles_menu.append(menu_item)
        menu_item.show()

        for profile in Profile.iter_profiles():
            title = '%s@%s (%s)' % (profile.user_name, profile.org_name,
                profile.server_name)

            if profile.status:
                menu_item = gtk.MenuItem(title)
                menu.append(menu_item)
                menu_item.show()

            menu_item = gtk.CheckMenuItem(title)
            menu_item.set_active(profile.status)
            menu_item.connect('activate', self.on_toggle_profile, profile)
            profiles_menu.append(menu_item)
            menu_item.show()

        if not len(menu):
            conn_active = False
            menu_item = gtk.MenuItem('No Active Connections')
            menu_item.set_sensitive(False)
            menu.append(menu_item)
            menu_item.show()

        if len(profiles_menu) == 2:
            menu_item = gtk.MenuItem('No Profiles Available')
            menu_item.set_sensitive(False)
            profiles_menu.append(menu_item)
            menu_item.show()

        if conn_active:
            menu_item = gtk.SeparatorMenuItem()
            profiles_menu.append(menu_item)
            menu_item.show()

            menu_item = gtk.MenuItem('Disconnect All Profiles')
            menu_item.connect('activate', self.on_disconnect_all)
            profiles_menu.append(menu_item)
            menu_item.show()

        menu_item = gtk.SeparatorMenuItem()
        menu.append(menu_item)
        menu_item.show()

        menu_item = gtk.MenuItem('Profiles')
        menu_item.set_submenu(profiles_menu)
        menu.append(menu_item)
        menu_item.show()

        menu_item = gtk.MenuItem('Import Profile')
        menu_item.connect('activate', self.show_import_profile)
        menu.append(menu_item)
        menu_item.show()

        menu_item = gtk.MenuItem('Import Profile URI')
        menu_item.connect('activate', self.show_import_profile_uri)
        menu.append(menu_item)
        menu_item.show()

        menu_item = gtk.MenuItem('About')
        menu_item.connect('activate', self.show_about)
        menu.append(menu_item)
        menu_item.show()

        menu_item = gtk.MenuItem('Exit')
        menu_item.connect('activate', self.destroy)
        menu.append(menu_item)
        menu_item.show()

        menu.popup(None, None, None, event_button, activate_time)

    def show_about(self, widget, data=None):
        # gtk.AboutDialog
        dialog = gtk.MessageDialog(buttons=gtk.BUTTONS_OK,
            message_format='Pritunl Client')
        dialog.set_title('Pritunl - About')
        dialog.run()
        dialog.destroy()

    def show_import_profile(self, widget):
        dialog = gtk.FileChooserDialog('Select profile to import...',
            buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        dialog.set_title('Pritunl - Import Profile')

        profile_filter = gtk.FileFilter()
        profile_filter.set_name('Pritunl Profile')
        profile_filter.add_pattern('*.ovpn')
        profile_filter.add_pattern('*.conf')
        profile_filter.add_pattern('*.tar')
        dialog.add_filter(profile_filter)

        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            profile_path = dialog.get_filename()
        dialog.destroy()

    def show_import_profile_uri(self, widget):
        dialog = gtk.MessageDialog(
            type=gtk.MESSAGE_QUESTION,
            buttons=gtk.BUTTONS_OK_CANCEL,
            message_format='Import Profile URI')
        dialog.format_secondary_markup('Enter profile URI to import...')
        dialog.set_title('Pritunl - Import Profile URI')

        entry = gtk.Entry()
        entry.set_width_chars(32)

        hbox = gtk.HBox()
        hbox.pack_start(gtk.Label('Profile URI:'), False, 5, 5)
        hbox.pack_end(entry)

        dialog.vbox.pack_end(hbox, True, True, 0)
        dialog.show_all()

        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            profile_uri = entry.get_text()
        dialog.destroy()

    def destroy(self, widget):
        gtk.main_quit()

    def main(self):
        gtk.main()
