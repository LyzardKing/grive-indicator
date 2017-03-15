#!/usr/bin/env python3

import os
import gi
import re
import shutil
import site
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import json
import subprocess
import logging
from grive_indicator.tools import runConfigure
from grive_indicator import UI


logger = logging.getLogger(__name__)


class ConfigureWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Configure")

        hb = Gtk.HeaderBar()
        hb.set_show_close_button(False)
        hb.props.title = "HeaderBar example"
        self.set_titlebar(hb)

        self.set_border_width(6)

        grid = Gtk.Grid()
        self.add(grid)

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

        grid.add(label_folder)
        grid.attach(self.folder_chooser, 1, 0, 2, 1)
        grid.attach_next_to(label_selective, label_folder, Gtk.PositionType.BOTTOM, 1, 1)
        grid.attach_next_to(self.remote_folder, label_selective, Gtk.PositionType.RIGHT, 2, 1)
        grid.attach_next_to(confirm_button, self.remote_folder, Gtk.PositionType.BOTTOM, 1, 1)
        grid.attach_next_to(escape_button, confirm_button, Gtk.PositionType.RIGHT, 2, 1)

    def confirmSettings(self, widget):
        folder_chooser = self.folder_chooser.get_filename()
        remote_folder = self.remote_folder.get_text()
        runConfigure(folder_chooser, remote_folder)
        response = UI.InfoDialog.main(self, "Restart grive-indicator to start auto sync")
        if response == Gtk.ResponseType.OK:
            Gtk.main_quit()

    def cancel(self, widget):
        Gtk.main_quit()


def main():
    window = ConfigureWindow()
    window.connect("delete-event", Gtk.main_quit)
    window.show_all()
