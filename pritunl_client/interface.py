from constants import *
from profile import Profile
import utils
import threading
import time
import pygtk
pygtk.require('2.0')
import gtk

HAS_APPINDICATOR = False
try:
    import appindicator
    HAS_APPINDICATOR = True
except ImportError:
    pass

gtk.threads_init()
gtk.threads_enter()

class Interface:
    def __init__(self):
        if HAS_APPINDICATOR:
            self.icon = appindicator.Indicator('pritunl_client',
                utils.get_disconnected_logo(),
                appindicator.CATEGORY_APPLICATION_STATUS)
            self.icon.set_status(appindicator.STATUS_ACTIVE)
            self.update_menu()
        else:
            self.icon = gtk.StatusIcon()
            self.icon.set_tooltip('Pritunl Client')
            self.icon.connect('activate', self.on_click_left)
            self.icon.connect('popup_menu', self.on_click_right)
        self._cur_icon_path = utils.get_disconnected_logo()
        self.icon_state = None
        self.set_icon_state(False)

    def set_icon_state(self, state, force=False):
        if state == self.icon_state and not force:
            return

        self.icon_state = state
        if HAS_APPINDICATOR:
            set_icon = self.icon.set_icon
        else:
            set_icon = self.icon.set_from_file
        if state:
            set_icon(utils.get_connected_logo())
        else:
            set_icon(utils.get_disconnected_logo())

    def get_icon_state(self):
        return self.icon_state

    def on_click_left(self, widget):
        self.show_menu(0, 0)

    def on_click_right(self, widget, button, activate_time):
        self.show_menu(button, gtk.gdk.CURRENT_TIME)

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

    def on_status_change(self):
        conn_count = 0
        active_count = 0

        for profile in Profile.iter_profiles():
            if profile.status == CONNECTED:
                conn_count += 1
            if profile.status in (CONNECTING, RECONNECTING, CONNECTED):
                active_count += 1

        self.set_icon_state(bool(conn_count))
        self.update_menu()

    def on_connect_profile(self, widget, profile_id):
        profile = Profile.get_profile(profile_id)
        if profile.status not in (DISCONNECTED, ENDED):
            return

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

        def connect_callback():
            dialog.destroy()

        threading.Thread(target=profile.start,
            args=(self.on_status_change, connect_callback)).start()

        response = dialog.run()
        dialog.destroy()
        if response == gtk.RESPONSE_CANCEL:
            threading.Thread(target=profile.stop).start()
            return

        if profile.status == DISCONNECTED:
            self.show_connect_error(profile)

    def on_disconnect_profile(self, widget, profile_id):
        profile = Profile.get_profile(profile_id)
        profile.stop()

    def on_rename_profile(self, widget, profile_id):
        profile = Profile.get_profile(profile_id)
        dialog = gtk.MessageDialog(
            type=gtk.MESSAGE_QUESTION,
            buttons=gtk.BUTTONS_OK_CANCEL,
            message_format='Rename Profile')
        dialog.format_secondary_markup('Enter new name for profile %s' % (
            profile.name))
        dialog.set_title('Pritunl - Rename Profile')

        entry = gtk.Entry()
        entry.set_width_chars(32)

        hbox = gtk.HBox()
        hbox.pack_start(gtk.Label('Profile Name:'), False, 5, 5)
        hbox.pack_end(entry)

        dialog.vbox.pack_end(hbox, True, True, 0)
        dialog.show_all()

        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            new_name = entry.get_text()
            profile.set_name(new_name[:32])
            self.update_menu()
        dialog.destroy()

    def on_delete_profile(self, widget, profile_id):
        profile = Profile.get_profile(profile_id)
        dialog = gtk.MessageDialog(
            type=gtk.MESSAGE_ERROR,
            buttons=gtk.BUTTONS_OK_CANCEL,
            message_format='Delete profile')
        dialog.format_secondary_markup(
            'Are you sure you want to delete the profile %s' % profile.name)
        dialog.set_title('Pritunl - Delete Profile')
        dialog.show_all()

        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            profile.delete()
            self.update_menu()
        dialog.destroy()

    def on_autostart_profile(self, widget, profile_id):
        profile = Profile.get_profile(profile_id)
        profile.set_autostart(True)

    def on_no_autostart_profile(self, widget, profile_id):
        profile = Profile.get_profile(profile_id)
        profile.set_autostart(False)

    def on_disconnect_all(self, widget):
        for profile in Profile.iter_profiles():
            profile.stop()

    def _build_menu(self):
        menu = gtk.Menu()
        profiles_menu = gtk.Menu()
        conn_active = True

        menu_item = gtk.MenuItem('Toggle Profile Connections')
        menu_item.set_sensitive(False)
        profiles_menu.append(menu_item)

        menu_item = gtk.SeparatorMenuItem()
        profiles_menu.append(menu_item)

        for profile in Profile.iter_profiles():
            active = False

            if profile.status in (CONNECTING, RECONNECTING, CONNECTED):
                active = True
                menu_item = gtk.MenuItem(
                    profile.name + ' - %s' % profile.status.capitalize())
                menu.append(menu_item)

            profile_menu = gtk.Menu()

            menu_item = gtk.CheckMenuItem(
                'Disconnect' if active else 'Connect')
            menu_item.set_active(active)
            menu_item.connect('activate', self.on_disconnect_profile if
                active else self.on_connect_profile, profile.id)
            profile_menu.append(menu_item)

            menu_item = gtk.MenuItem('Rename')
            menu_item.connect('activate', self.on_rename_profile, profile.id)
            profile_menu.append(menu_item)

            menu_item = gtk.MenuItem('Delete')
            menu_item.connect('activate', self.on_delete_profile, profile.id)
            profile_menu.append(menu_item)

            menu_item = gtk.CheckMenuItem('Autostart')
            menu_item.set_active(profile.autostart)
            menu_item.connect('activate', self.on_no_autostart_profile if
                profile.autostart else self.on_autostart_profile, profile.id)
            profile_menu.append(menu_item)

            menu_item = gtk.MenuItem(profile.name)
            menu_item.set_submenu(profile_menu)
            profiles_menu.append(menu_item)

        if not len(menu):
            conn_active = False
            menu_item = gtk.MenuItem('No Active Connections')
            menu_item.set_sensitive(False)
            menu.append(menu_item)

        if len(profiles_menu) == 2:
            menu_item = gtk.MenuItem('No Profiles Available')
            menu_item.set_sensitive(False)
            profiles_menu.append(menu_item)

        if conn_active:
            menu_item = gtk.SeparatorMenuItem()
            profiles_menu.append(menu_item)

            menu_item = gtk.MenuItem('Disconnect All Profiles')
            menu_item.connect('activate', self.on_disconnect_all)
            profiles_menu.append(menu_item)

        menu_item = gtk.SeparatorMenuItem()
        menu.append(menu_item)

        menu_item = gtk.MenuItem('Profiles')
        menu_item.set_submenu(profiles_menu)
        menu.append(menu_item)

        menu_item = gtk.MenuItem('Import Profile')
        menu_item.connect('activate', self.show_import_profile)
        menu.append(menu_item)

        menu_item = gtk.MenuItem('Import Profile URI')
        menu_item.connect('activate', self.show_import_profile_uri)
        menu.append(menu_item)

        menu_item = gtk.MenuItem('About')
        menu_item.connect('activate', self.show_about)
        menu.append(menu_item)

        menu_item = gtk.MenuItem('Exit')
        menu_item.connect('activate', self.destroy)
        menu.append(menu_item)

        def _toggle_icon(widget):
            self.set_icon_state(not self.get_icon_state())
        menu_item = gtk.MenuItem('Toggle Icon State (Debug)')
        menu_item.connect('activate', _toggle_icon)
        menu.append(menu_item)

        menu.show_all()
        return menu

    def show_menu(self, event_button, activate_time):
        self.update_icon()
        menu = self._build_menu()
        menu.popup(None, None, None, event_button, activate_time)

    def update_menu(self):
        self.update_icon()
        if HAS_APPINDICATOR:
            self.icon.set_menu(self._build_menu())

    def update_icon(self):
        icon_path = utils.get_disconnected_logo()
        if self._cur_icon_path != icon_path:
            self._cur_icon_path = icon_path
            self.set_icon_state(self.get_icon_state(), True)

    def show_about(self, widget, data=None):
        import pritunl_client
        dialog = gtk.MessageDialog(buttons=gtk.BUTTONS_OK)
        dialog.set_title('Pritunl - About')
        dialog.set_markup(('<b>Pritunl Client - v%s</b>\n\n' +
            'Copyright (c) 2013 Zachary Huff\n\n' +
            'http://pritunl.com/') % pritunl_client.__version__)

        pix_buf = gtk.gdk.pixbuf_new_from_file(utils.get_logo())
        pix_buf = pix_buf.scale_simple(90, 90, gtk.gdk.INTERP_BILINEAR)
        image = gtk.Image()
        image.set_from_pixbuf(pix_buf)
        image.show()
        dialog.set_image(image)

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
            with open(profile_path, 'r') as profile_file:
                profile = Profile.get_profile()
                profile.write(profile_file.read())
                self.update_menu()
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
            self.update_menu()
        dialog.destroy()

    def autostart(self):
        time.sleep(0.3)
        for profile in Profile.iter_profiles():
            if not profile.autostart:
                continue
            threading.Thread(target=profile.start_autostart,
                args=(self.on_status_change,)).start()

    def destroy(self, widget):
        self.icon.set_visible(False)
        gtk.main_quit()

    def main(self):
        try:
            thread = threading.Thread(target=self.autostart)
            thread.daemon = True
            thread.start()
            gtk.main()
            gtk.threads_leave()
        finally:
            for profile in Profile.iter_profiles():
                profile.stop()
