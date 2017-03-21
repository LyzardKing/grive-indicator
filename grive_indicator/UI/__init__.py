#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import logging

logger = logging.getLogger(__name__)


class CSDWindow(Gtk.Window):

    def __init__(self, title):
        Gtk.Window.__init__(self, title=title)

        self.set_default_size(150, 100)
        self.set_border_width(6)

        hb = Gtk.HeaderBar()
        hb.set_show_close_button(False)
        hb.props.title = title
        self.set_titlebar(hb)

        self.set_border_width(6)

        self.grid = Gtk.Grid()
        self.add(self.grid)


class CSDDialog(Gtk.Dialog):

    def __init__(self, parent, title, label, input):
        Gtk.Dialog.__init__(self, title, parent, 0,
                            (Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.set_default_size(150, 100)
        self.set_border_width(6)

        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        hb.props.title = title
        self.set_titlebar(hb)


class InfoDialog(CSDDialog):

    def __init__(self, parent, title, label, input=False):
        super().__init__(parent, title, label, input)

        label = Gtk.Label(label)

        box = self.get_content_area()
        box.add(label)
        self.show_all()

    def main(parent, title, label):
        dialog = InfoDialog(parent=parent, title=title, label=label)
        response = dialog.run()
        dialog.destroy()
        return response


class EntryDialog(CSDDialog):

    def __init__(self, parent, title, label, input=False):
        super().__init__(parent, title, label, input)

        self.entry = Gtk.Entry()

        box = self.get_content_area()
        box.add(self.entry)
        self.show_all()

    def main(parent, title, label):
        dialog = EntryDialog(parent=parent, title=title, label=label)
        dialog.run()
        return dialog.entry.get_text()
