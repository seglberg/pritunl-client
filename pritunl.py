import pygtk
pygtk.require('2.0')
import gtk

class Pritunl:
    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title('Pritunl Client')
        self.window.set_border_width(10)
        self.window.set_size_request(375, 400)
        self.window.connect('delete_event', self.delete_event)
        self.window.connect('destroy', self.destroy)

        self.window_vbox = gtk.VBox(False, 0)
        self.window.add(self.window_vbox)


        self.profiles_window = gtk.ScrolledWindow()
        self.profiles_window.set_border_width(10)
        self.profiles_window.set_policy(
            gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
        self.window_vbox.pack_start(self.profiles_window, True, True, 0)
        self.profiles_window.show()

        self.profiles_table = gtk.Table(100, 1, False)
        self.profiles_table.set_row_spacings(10)
        self.profiles_table.set_col_spacings(10)
        self.profiles_window.add_with_viewport(self.profiles_table)
        self.profiles_table.show()


        self.button_box = gtk.HBox(True, 5)
        self.button_box.set_size_request(-1, 50)
        self.window_vbox.pack_start(self.button_box, False, False, 0)

        add_button = gtk.Button('Add')
        add_button.connect('clicked', self.add, None)
        self.button_box.pack_start(add_button, True, True, 0)
        add_button.show()

        remove_button = gtk.Button('Remove')
        remove_button.connect('clicked', self.remove, None)
        self.button_box.pack_start(remove_button, True, True, 0)
        remove_button.show()

        self.button_box.show()


        self.window_vbox.show()
        self.window.show()

    def add(self, widget, data=None):
        print 'add'

    def remove(self, widget, data=None):
        print 'remove'

    def delete_event(self, widget, event, data=None):
        return False

    def destroy(self, widget, data=None):
        gtk.main_quit()

    def main(self):
        gtk.main()

if __name__ == '__main__':
    pritunl = Pritunl()
    pritunl.main()
