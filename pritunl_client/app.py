from constants import *
from profile import Profile
import interface
import utils
import threading
import time
import sys
import tarfile

class App:
    def __init__(self):
        if PLATFORM == WIN:
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

        self._icon_state = None
        self._cur_icon_path = None
        self.icon = interface.StatusIconApp()
        self.icon.set_tooltip(APP_NAME_FORMATED)
        self.set_icon_state(False)
        self.icon.set_callback(self.update_icon)
        self.update_menu()

    def set_icon_state(self, state):
        self._icon_state = state
        if state:
            self.icon.set_icon(utils.get_connected_logo())
        else:
            self.icon.set_icon(utils.get_disconnected_logo())

    def get_icon_state(self):
        return self._icon_state

    def toggle_icon_state(self):
        self.set_icon_state(not self.get_icon_state())

    def update_menu(self):
        self.update_icon()
        menu = interface.Menu()
        profile_count = 0

        for profile in Profile.iter_profiles():
            profile_count += 1
            active = profile.status in ACTIVE_STATES

            profile_menu = interface.Menu()
            if active:
                profile_menu.set_label(
                    profile.name + ' - %s' % profile.status.capitalize())
            else:
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

            if not profile.auth_passwd:
                menu_item = interface.CheckMenuItem()
                menu_item.set_label('Autostart')
                menu_item.set_active(profile.autostart)
                menu_item.set_callback(self.on_no_autostart_profile if
                    profile.autostart else self.on_autostart_profile,
                    profile.id)
                profile_menu.add_item(menu_item)

            menu.add_item(profile_menu)

        if not profile_count:
            menu_item = interface.MenuItem()
            menu_item.set_label('No Profiles Available')
            menu_item.set_state(False)
            menu.add_item(menu_item)

        menu_item = interface.SeparatorMenuItem()
        menu.add_item(menu_item)

        menu_item = interface.MenuItem()
        menu_item.set_label('Import Profile')
        menu_item.set_callback(self.show_import_profile)
        menu.add_item(menu_item)

        # menu_item = interface.MenuItem()
        # menu_item.set_label('Import Profile URI')
        # menu_item.set_callback(self.show_import_profile_uri)
        # menu.add_item(menu_item)

        menu_item = interface.MenuItem()
        menu_item.set_label('About')
        menu_item.set_callback(self.show_about)
        menu.add_item(menu_item)

        menu_item = interface.MenuItem()
        menu_item.set_label('Exit')
        menu_item.set_callback(self.exit)
        menu.add_item(menu_item)

        self.icon.set_menu(menu)

    def update_icon(self):
        icon_path = utils.get_disconnected_logo()
        if self._cur_icon_path != icon_path:
            self._cur_icon_path = icon_path
            self.set_icon_state(self.get_icon_state())

    def show_connect_error(self, profile, status):
        error_msgs = {
            ERROR: 'An error occurred while connecting to server',
            AUTH_ERROR: 'Failed to authenticate with server',
            TIMEOUT_ERROR: 'Server connection timed out',
        }

        dialog = interface.MessageDialog()
        dialog.set_type(MESSAGE_ERROR)
        dialog.set_buttons(BUTTONS_OK)
        dialog.set_title(APP_NAME_FORMATED)
        dialog.set_icon(utils.get_logo())
        dialog.set_message('Unable to connect to %s' % profile.server_name)
        dialog.set_message_secondary(error_msgs[status])
        dialog.run()
        dialog.destroy()

    def on_status_change(self):
        conn_count = 0
        active_count = 0

        for profile in Profile.iter_profiles():
            if profile.status == CONNECTED:
                conn_count += 1
            if profile.status in ACTIVE_STATES:
                active_count += 1

        self.set_icon_state(bool(conn_count))
        self.update_menu()

    def on_connect_profile(self, profile_id):
        passwd = None
        profile = Profile.get_profile(profile_id)
        if profile.status in ACTIVE_STATES:
            return

        if profile.auth_passwd:
            dialog = interface.InputDialog()
            dialog.set_title(APP_NAME_FORMATED)
            dialog.set_icon(utils.get_logo())
            dialog.set_message('Profile Authenticator Required')
            dialog.set_message_secondary('Enter authenticator key for %s' % (
                profile.name))
            dialog.set_input_label('Authenticator Key:')
            dialog.set_input_width(16)
            passwd = dialog.run()
            dialog.destroy()
            if passwd is None:
                return

        dialog = interface.MessageDialog()
        dialog.set_type(MESSAGE_LOADING)
        dialog.set_buttons(BUTTONS_CANCEL)
        dialog.set_title(APP_NAME_FORMATED)
        dialog.set_icon(utils.get_logo())
        dialog.set_message('Connecting to %s' % profile.server_name)
        dialog.set_message_secondary('Conecting to the server...')

        def connect_callback():
            dialog.close()

        threading.Thread(target=profile.start,
            args=(self.on_status_change, connect_callback, passwd)).start()

        response = dialog.run()
        dialog.destroy()
        if response is False:
            threading.Thread(target=profile.stop).start()
            return

        if profile.status in ERROR_STATES:
            self.show_connect_error(profile, profile.status)

    def on_disconnect_profile(self, profile_id):
        profile = Profile.get_profile(profile_id)
        profile.stop()

    def on_rename_profile(self, profile_id):
        profile = Profile.get_profile(profile_id)
        dialog = interface.InputDialog()
        dialog.set_title(APP_NAME_FORMATED)
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
        dialog.set_title(APP_NAME_FORMATED)
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
        dialog.set_title(APP_NAME_FORMATED)
        dialog.set_icon(utils.get_logo())
        dialog.set_image(utils.get_logo())
        dialog.set_message(('<b>%s - v%s</b>\n\n' +
            'Copyright (c) 2013-2014 Pritunl\n\n' +
            'http://pritunl.com/') % (APP_NAME_FORMATED,
            pritunl_client.__version__))
        dialog.run()
        dialog.destroy()

    def show_import_profile(self):
        dialog = interface.FileChooserDialog()
        dialog.set_title(APP_NAME_FORMATED)
        dialog.set_icon(utils.get_logo())
        dialog.add_filter('Pritunl Profile', '*.ovpn')
        dialog.add_filter('Pritunl Profile', '*.conf')
        dialog.add_filter('Pritunl Profile', '*.tar')

        response = dialog.run()
        dialog.destroy()
        if response:
            if os.path.splitext(response)[1] == '.tar':
                tar = tarfile.open(response)
                for member in tar:
                    profile = Profile.get_profile()
                    profile.write_profile(tar.extractfile(member).read())
            else:
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

    def exit(self):
        for profile in Profile.iter_profiles():
            profile.stop()
        self.icon.destroy()
        sys.exit(0)

    def main(self):
        try:
            thread = threading.Thread(target=self.autostart)
            thread.daemon = True
            thread.start()
            self.icon.run()
        finally:
            for profile in Profile.iter_profiles():
                profile.stop()
            self.icon.destroy()
