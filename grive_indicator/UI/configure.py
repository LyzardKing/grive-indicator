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
from grive_indicator.tools import runConfigure
from grive_indicator.UI import InfoDialog, CSDWindow


logger = logging.getLogger(__name__)


class ConfigureWindow(Gtk.Window):

    def __init__(self):
        super().__init__(title='Settings')

        label_folder = Gtk.Label("Local Folder")
        self.folder_chooser = Gtk.FileChooserButton(action=Gtk.FileChooserAction.SELECT_FOLDER)

        label_selective = Gtk.Label("Remote Folder (leave blank for all)")
        self.remote_folder = Gtk.Entry()

        confirm_button = Gtk.Button('Ok')
        confirm_button.connect('clicked',
                               self.confirmSettings)

        escape_button = Gtk.Button('Cancel')
        escape_button.connect('clicked',
                              self.cancel)

        self.grid.add(label_folder)
        self.grid.attach(self.folder_chooser, 1, 0, 2, 1)
        self.grid.attach_next_to(label_selective, label_folder, Gtk.PositionType.BOTTOM, 1, 1)
        self.grid.attach_next_to(self.remote_folder, label_selective, Gtk.PositionType.RIGHT, 2, 1)
        self.grid.attach_next_to(confirm_button, self.remote_folder, Gtk.PositionType.BOTTOM, 1, 1)
        self.grid.attach_next_to(escape_button, confirm_button, Gtk.PositionType.RIGHT, 2, 1)

    def confirmSettings(self, widget):
        folder_chooser = self.folder_chooser.get_filename()
        remote_folder = self.remote_folder.get_text()
        runConfigure(folder_chooser, remote_folder)
        response = InfoDialog.main(self, "Restart grive-indicator to start auto sync")
        if response == Gtk.ResponseType.OK:
            Gtk.main_quit()

    def cancel(self, widget):
        Gtk.main_quit()


def main():
    window = ConfigureWindow()
    window.connect("delete-event", Gtk.main_quit)
    window.show_all()
