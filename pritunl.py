import pygtk
pygtk.require('2.0')
import gtk

class Pritunl:
    def __init__(self):
        icon = gtk.status_icon_new_from_stock(gtk.STOCK_ABOUT)
        icon.connect('activate', self.on_click_left)
        icon.connect('popup_menu', self.on_click_right)

    def on_click_left(self, widget):
        self.show_menu(0, 0)

    def on_click_right(self, widget, button, activate_time):
        self.show_menu(button, gtk.gdk.CURRENT_TIME)

    def show_menu(self, event_button, activate_time, data=None):
        menu = gtk.Menu()

        menu_item = gtk.MenuItem('No Profiles Available')
        menu_item.set_sensitive(False)
        menu.append(menu_item)
        menu_item.show()

        # for i in xrange(4):
        #     menu_item = gtk.CheckMenuItem('Example Profile %s' % i)
        #     # menu_item.set_active(True)
        #     menu.append(menu_item)
        #     menu_item.show()

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
        dialog.run()
        dialog.destroy()

    def show_import_profile(self, widget, data=None):
        dialog = gtk.FileChooserDialog('Select profile to import...',
            buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                gtk.STOCK_OPEN, gtk.RESPONSE_OK))

        profile_filter = gtk.FileFilter()
        profile_filter.set_name('Pritunl Profile')
        profile_filter.add_pattern('*.ovpn')
        profile_filter.add_pattern('*.conf')
        dialog.add_filter(profile_filter)

        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            profile_path = dialog.get_filename()
        dialog.destroy()

    def show_import_profile_uri(self, widget, data=None):
        dialog = gtk.MessageDialog(
            type=gtk.MESSAGE_QUESTION,
            buttons=gtk.BUTTONS_OK_CANCEL,
            message_format='Import Profile URI')
        dialog.format_secondary_markup('Enter profile URI to import...')

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

    def destroy(self, widget, data=None):
        gtk.main_quit()

    def main(self):
        gtk.main()

if __name__ == '__main__':
    pritunl = Pritunl()
    pritunl.main()
