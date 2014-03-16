import pygtk
pygtk.require('2.0')
import gtk
import gobject
import os
import uuid
import json
import time
import subprocess
import threading

gtk.gdk.threads_init()

CONF_DIR = os.path.expanduser('~/.config/pritunl')
PROFILES_DIR = os.path.join(CONF_DIR, 'profiles')
CONNECT_TIMEOUT = 30
OVPN_EXIT_TIMEOUT = 5

_connections = {}

class Profile:
    def __init__(self, id=None):
        if id:
            self.id = id
        else:
            self.id = uuid.uuid4()
        self._loaded = False

        self.user_name = None
        self.org_name = None
        self.server_name = None

        if not os.path.isdir(PROFILES_DIR):
            os.makedirs(PROFILES_DIR)

        self.path = os.path.join(PROFILES_DIR, '%s.ovpn' % self.id)

        if id:
            self.load()

    def __getattr__(self, name):
        if name in ('user_name', 'org_name', 'server_name'):
            self._load()
        elif name == 'status':
            connection_data = _connections.get(self.id)
            if connection_data:
                return connection_data.get('status', False)
            return False
        elif name not in self.__dict__:
            raise AttributeError('Config instance has no attribute %r' % name)
        return self.__dict__[name]

    def load(self):
        self.user_name = None
        self.org_name = None
        self.server_name = None

        with open(self.path, 'r') as profile_file:
            info_str = profile_file.readline().replace('#', '', 1).strip()
            try:
                info_data = json.loads(info_str)
            except ValueError:
                return
            if 'user' in info_data:
                self.user_name = info_data['user']
            if 'organization' in info_data:
                self.org_name = info_data['organization']
            if 'server' in info_data:
                self.server_name = info_data['server']

    def write(self, data):
        with open(self.path, 'w') as profile_file:
            profile_file.write(data)

    def start(self, status_callback, dialog_callback):
        process = subprocess.Popen(['gksudo', 'openvpn %s' % self.path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        data = {
            'status': False,
            'process': process,
            'status_callback': status_callback,
            'dialog_callback': dialog_callback,
        }
        _connections[self.id] = data

        def change_status(status):
            data['status'] = status
            if data['dialog_callback']:
                callback = data['dialog_callback']
                data['dialog_callback'] = None
                gobject.idle_add(callback, self)
            gobject.idle_add(data['status_callback'], self)

        def poll_thread():
            while True:
                line = process.stdout.readline()
                print line.strip()
                if not line:
                    if process.poll() is not None:
                        break
                    else:
                        continue
                if 'Initialization Sequence Completed' in line:
                    change_status(True)
                elif 'Inactivity timeout' in line:
                    change_status(False)
            change_status(False)
            data.pop(self.id, None)

        def dialog_thread():
            time.sleep(CONNECT_TIMEOUT)
            if not data['dialog_callback']:
                return
            self.stop()

        thread = threading.Thread(target=poll_thread)
        thread.daemon = True
        thread.start()

        thread = threading.Thread(target=dialog_thread)
        thread.daemon = True
        thread.start()

    def stop(self):
        connection_data = _connections.get(self.id)
        if connection_data:
            process = connection_data.get('process')
            if process:
                process.terminate()
                for i in xrange(int(OVPN_EXIT_TIMEOUT / 0.1)):
                    time.sleep(0.1)
                    if process.poll() is not None:
                        break
                    process.terminate()
                if process.poll() is not None:
                    return

                process.kill()
                for i in xrange(int(OVPN_EXIT_TIMEOUT / 0.1)):
                    time.sleep(0.1)
                    if process.poll() is not None:
                        break
                    process.kill()

    @classmethod
    def iter_profiles(cls):
        if os.path.isdir(PROFILES_DIR):
            for profile_id in os.listdir(PROFILES_DIR):
                profile_id = profile_id.replace('.ovpn', '')
                yield Profile(profile_id)

class Pritunl:
    def __init__(self):
        icon = gtk.status_icon_new_from_stock(gtk.STOCK_ABOUT)
        icon.connect('activate', self.on_click_left)
        icon.connect('popup_menu', self.on_click_right)

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
        print 'STATUS:', profile.status

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

    def show_menu(self, event_button, activate_time):
        menu = gtk.Menu()

        for profile in Profile.iter_profiles():
            menu_item = gtk.CheckMenuItem('%s@%s (%s)' % (
                profile.user_name, profile.org_name, profile.server_name))
            menu_item.connect('activate', self.on_toggle_profile, profile)
            # menu_item.set_active(True)
            menu.append(menu_item)
            menu_item.show()

        if not len(menu):
            menu_item = gtk.MenuItem('No Profiles Available')
            menu_item.set_sensitive(False)
            menu.append(menu_item)
            menu_item.show()

        menu_item = gtk.SeparatorMenuItem()
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

if __name__ == '__main__':
    pritunl = Pritunl()
    pritunl.main()
