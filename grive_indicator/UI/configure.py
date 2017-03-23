#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import gi
import re
import shutil
import site
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import subprocess
import logging
from ..tools import runConfigure
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
        self.remote_folder.get_buffer().set_text("# Set rules For selective sync.\n"
                                                 "# Check the man page or"
                                                 "https://github.com/vitalif/grive2#griveignore.")
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
