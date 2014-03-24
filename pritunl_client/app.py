from constants import *
from profile import Profile
import interface
import utils
import threading
import time

class App:
    def __init__(self):
        self._icon_state = None
        self._cur_icon_path = None
        self.icon = interface.StatusIconApp()
        self.icon.set_tooltip(APP_NAME_FORMATED)
        self.set_icon_state(False)
        self.update_menu()

    def set_icon_state(self, state):
        self._icon_state = state
        if state:
            self.icon.set_icon(utils.get_connected_logo())
        else:
            self.icon.set_icon(utils.get_disconnected_logo())

    def get_icon_state(self):
        return self._icon_state

    def update_menu(self):
        self.update_icon()
        menu = interface.Menu()
        # TODO move profiles to main menu
        profiles_menu = interface.Menu()
        profiles_menu.set_label('Profiles')
        conn_active = False
        profile_count = 0

        for profile in Profile.iter_profiles():
            profile_count += 1
            active = False

            if profile.status in (CONNECTING, RECONNECTING, CONNECTED):
                active = True
                conn_active = True
                menu_item = interface.MenuItem()
                menu_item.set_label(
                    profile.name + ' - %s' % profile.status.capitalize())
                menu.add_item(menu_item)

            profile_menu = interface.Menu()
            profile_menu.set_label(profile.name)

            menu_item = interface.MenuItem()
            menu_item.set_label('Disconnect' if active else 'Connect')
            menu_item.set_callback(self.on_disconnect_profile if
                active else self.on_connect_profile, profile.id)
            profile_menu.add_item(menu_item)

            menu_item = interface.MenuItem()
            menu_item.set_label('Rename')
            menu_item.set_callback(self.on_rename_profile, profile.id)
            profile_menu.add_item(menu_item)

            menu_item = interface.MenuItem()
            menu_item.set_label('Delete')
            menu_item.set_callback(self.on_delete_profile, profile.id)
            profile_menu.add_item(menu_item)

            menu_item = interface.CheckMenuItem()
            menu_item.set_label('Autostart')
            menu_item.set_active(profile.autostart)
            menu_item.set_callback(self.on_no_autostart_profile if
                profile.autostart else self.on_autostart_profile, profile.id)
            profile_menu.add_item(menu_item)

            profiles_menu.add_item(profile_menu)

        if not conn_active:
            menu_item = interface.MenuItem()
            menu_item.set_label('No Active Connections')
            menu_item.set_state(False)
            menu.add_item(menu_item)

        menu_item = interface.SeparatorMenuItem()
        menu.add_item(menu_item)

        if not profile_count:
            menu_item = interface.MenuItem()
            menu_item.set_label('No Profiles Available')
            menu_item.set_state(False)
            profiles_menu.add_item(menu_item)

        menu.add_item(profiles_menu)

        menu_item = interface.MenuItem()
        menu_item.set_label('Import Profile')
        menu_item.set_callback(self.show_import_profile)
        menu.add_item(menu_item)

        menu_item = interface.MenuItem()
        menu_item.set_label('Import Profile URI')
        menu_item.set_callback(self.show_import_profile_uri)
        menu.add_item(menu_item)

        menu_item = interface.MenuItem()
        menu_item.set_label('About')
        menu_item.set_callback(self.show_about)
        menu.add_item(menu_item)

        menu_item = interface.MenuItem()
        menu_item.set_label('Exit')
        menu_item.set_callback(self.icon.destroy)
        menu.add_item(menu_item)

        self.icon.set_menu(menu)

    def update_icon(self):
        icon_path = utils.get_disconnected_logo()
        if self._cur_icon_path != icon_path:
            self._cur_icon_path = icon_path
            self.set_icon_state(self.get_icon_state())

    def show_connect_error(self, profile):
        dialog = interface.MessageDialog()
        dialog.set_type(MESSAGE_ERROR)
        dialog.set_buttons(BUTTONS_OK)
        dialog.set_title('%s - Connection Error' % APP_NAME_FORMATED)
        dialog.set_icon(utils.get_logo())
        dialog.set_message('Unable to connect to %s' % profile.server_name)
        dialog.set_message_secondary(
            'An error occurred while connecting to server')
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

    def on_connect_profile(self, profile_id):
        profile = Profile.get_profile(profile_id)
        if profile.status not in (DISCONNECTED, ENDED):
            return

        dialog = interface.MessageDialog()
        dialog.set_type(MESSAGE_LOADING)
        dialog.set_buttons(BUTTONS_CANCEL)
        dialog.set_title('%s - Connecting...' % APP_NAME_FORMATED)
        dialog.set_icon(utils.get_logo())
        dialog.set_message('Connecting to %s' % profile.server_name)
        dialog.set_message_secondary('Conecting to the server...')

        def connect_callback():
            dialog.destroy()

        threading.Thread(target=profile.start,
            args=(self.on_status_change, connect_callback)).start()

        response = dialog.run()
        dialog.destroy()
        if response is False:
            threading.Thread(target=profile.stop).start()
            return

        if profile.status == DISCONNECTED:
            self.show_connect_error(profile)

    def on_disconnect_profile(self, profile_id):
        profile = Profile.get_profile(profile_id)
        profile.stop()

    def on_rename_profile(self, profile_id):
        profile = Profile.get_profile(profile_id)
        dialog = interface.InputDialog()
        dialog.set_title('%s - Rename Profile' % APP_NAME_FORMATED)
        dialog.set_icon(utils.get_logo())
        dialog.set_message('Rename Profile')
        dialog.set_message_secondary('Enter new name for profile %s' % (
            profile.name))
        dialog.set_input_label('Profile Name:')
        dialog.set_input_width(32)
        response = dialog.run()
        dialog.destroy()
        if response is not None:
            profile.set_name(response[:32])
            self.update_menu()

    def on_delete_profile(self, profile_id):
        profile = Profile.get_profile(profile_id)
        dialog = interface.MessageDialog()
        dialog.set_type(MESSAGE_ERROR)
        dialog.set_buttons(BUTTONS_OK_CANCEL)
        dialog.set_title('%s - Delete Profile' % APP_NAME_FORMATED)
        dialog.set_icon(utils.get_logo())
        dialog.set_message('Delete profile')
        dialog.set_message_secondary(
            'Are you sure you want to delete the profile %s' % profile.name)
        response = dialog.run()
        dialog.destroy()
        if response:
            profile.delete()
            self.update_menu()

    def on_autostart_profile(self, profile_id):
        profile = Profile.get_profile(profile_id)
        profile.set_autostart(True)
        self.update_menu()

    def on_no_autostart_profile(self, profile_id):
        profile = Profile.get_profile(profile_id)
        profile.set_autostart(False)
        self.update_menu()

    def show_about(self):
        import pritunl_client
        dialog = interface.MessageDialog()
        dialog.set_type(MESSAGE_INFO)
        dialog.set_buttons(BUTTONS_OK)
        dialog.set_title('%s - About' % APP_NAME_FORMATED)
        dialog.set_icon(utils.get_logo())
        dialog.set_image(utils.get_logo())
        dialog.set_message(('<b>%s - v%s</b>\n\n' +
            'Copyright (c) 2013 Zachary Huff\n\n' +
            'http://pritunl.com/') % (APP_NAME_FORMATED,
            pritunl_client.__version__))
        dialog.run()
        dialog.destroy()

    def show_import_profile(self):
        dialog = interface.FileChooserDialog()
        dialog.set_title('%s - Import Profile' % APP_NAME_FORMATED)
        dialog.set_icon(utils.get_logo())
        dialog.add_filter('Pritunl Profile', '*.ovpn')
        dialog.add_filter('Pritunl Profile', '*.conf')
        dialog.add_filter('Pritunl Profile', '*.tar')

        response = dialog.run()
        dialog.destroy()
        if response:
            with open(response, 'r') as profile_file:
                profile = Profile.get_profile()
                profile.write_profile(profile_file.read())
                self.update_menu()

    def show_import_profile_uri(self):
        dialog = interface.InputDialog()
        dialog.set_title('%s - Import Profile URI' % APP_NAME_FORMATED)
        dialog.set_icon(utils.get_logo())
        dialog.set_message('Import Profile URI')
        dialog.set_message_secondary('Enter profile URI to import...')
        dialog.set_input_label('Profile URI:')
        dialog.set_input_width(32)
        response = dialog.run()
        dialog.destroy()
        if response:
            self.update_menu()

    def autostart(self):
        time.sleep(0.3)
        for profile in Profile.iter_profiles():
            if not profile.autostart:
                continue
            threading.Thread(target=profile.start_autostart,
                args=(self.on_status_change,)).start()

    def main(self):
        try:
            thread = threading.Thread(target=self.autostart)
            thread.daemon = True
            thread.start()
            self.icon.run()
        finally:
            for profile in Profile.iter_profiles():
                profile.stop()
