#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import logging
from grive_indicator.tools import ind

logger = logging.getLogger(__name__)


class CSDWindow(Gtk.Window):

    def __init__(self, title):
        Gtk.Window.__init__(self, title=title)
        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        hb.props.title = "HeaderBar example"
        self.set_titlebar(hb)


class Dialog(Gtk.Dialog):

    def __init__(self, parent, label):
        Gtk.Dialog.__init__(self, "My Dialog", parent, 0,
             (Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.set_default_size(150, 100)
        self.set_border_width(6)

        label = Gtk.Label(label)

        box = self.get_content_area()
        box.add(label)
        self.show_all()


def main(parent, label):
    dialog = Dialog(parent=parent, label=label)
    response = dialog.run()
    if response == Gtk.ResponseType.OK:
        Gtk.main_quit()