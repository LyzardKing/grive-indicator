# -*- coding: utf-8 -*-
# Copyright (C) 2017  Galileo Sartor
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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

        self.grid = Gtk.Grid(column_spacing=2, row_spacing=2)
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
