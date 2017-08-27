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
from ..tools import runConfigure, griveignore_init
from ..UI import InfoDialog, CSDWindow


logger = logging.getLogger(__name__)


class ConfigureWindow(CSDWindow):

    def __init__(self):
        super().__init__(title='Settings')

        label_folder = Gtk.Label("Local Folder")
        self.folder_chooser = Gtk.FileChooserButton(action=Gtk.FileChooserAction.SELECT_FOLDER)

        label_selective = Gtk.Label("Selective Sync (leave blank for all)")
        self.remote_folder = Gtk.TextView()
        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_hexpand(True)
        scrolledwindow.set_vexpand(True)
        self.remote_folder.get_buffer().set_text(griveignore_init)
        scrolledwindow.add(self.remote_folder)

        confirm_button = Gtk.Button('Ok')
        confirm_button.connect('clicked',
                               self.confirmSettings)

        escape_button = Gtk.Button('Cancel')
        escape_button.connect('clicked',
                              self.cancel)

        self.grid.add(label_folder)
        self.grid.attach(self.folder_chooser, 1, 0, 2, 1)
        self.grid.attach_next_to(label_selective, label_folder, Gtk.PositionType.BOTTOM, 1, 1)
        self.grid.attach_next_to(scrolledwindow, label_selective, Gtk.PositionType.RIGHT, 2, 1)
        self.grid.attach_next_to(confirm_button, scrolledwindow, Gtk.PositionType.BOTTOM, 1, 1)
        self.grid.attach_next_to(escape_button, confirm_button, Gtk.PositionType.RIGHT, 2, 1)

    def confirmSettings(self, widget):
        folder_chooser = self.folder_chooser.get_filename()
        selective_sync = self.remote_folder.get_buffer().get_text(self.remote_folder.get_buffer().get_start_iter(),
                                                                  self.remote_folder.get_buffer().get_end_iter(),
                                                                  True)
        # selective_sync = None if selective_sync is None else '*\n' + selective_sync
        runConfigure(folder_chooser, selective_sync)
        response = InfoDialog.main(parent=None, title='Warning', label="Restart grive-indicator to start auto sync")
        if response == Gtk.ResponseType.OK:
            Gtk.main_quit()

    def cancel(self, widget):
        Gtk.main_quit()


def main():
    window = ConfigureWindow()
    window.connect("delete-event", Gtk.main_quit)
    window.show_all()
