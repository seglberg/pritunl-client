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

        no_profiles_item = gtk.MenuItem('No Profiles Available')
        no_profiles_item.set_sensitive(False)
        menu.append(no_profiles_item)
        no_profiles_item.show()

        # for i in xrange(4):
        #     profile_item = gtk.CheckMenuItem('Example Profile %s' % i)
        #     # profile_item.set_active(True)
        #     menu.append(profile_item)
        #     profile_item.show()

        seperator_item = gtk.SeparatorMenuItem()
        menu.append(seperator_item)
        seperator_item.show()

        add_profile_item = gtk.MenuItem('Add Profile')
        menu.append(add_profile_item)
        add_profile_item.show()

        about_item = gtk.MenuItem('About')
        about_item.connect('activate', self.show_about)
        menu.append(about_item)
        about_item.show()

        exit_item = gtk.MenuItem('Exit')
        exit_item.connect('activate', self.destroy)
        menu.append(exit_item)
        exit_item.show()

        menu.popup(None, None, None, event_button, activate_time)

    def show_about(self, widget, data=None):
        msg_dialog = gtk.MessageDialog(buttons=gtk.BUTTONS_OK,
            message_format='Pritunl Client')
        msg_dialog.run()
        msg_dialog.destroy()

    def destroy(self, widget, data=None):
        gtk.main_quit()

    def main(self):
        gtk.main()

if __name__ == '__main__':
    pritunl = Pritunl()
    pritunl.main()
