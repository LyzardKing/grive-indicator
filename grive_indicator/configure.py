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
from grive_indicator.tools import getIcon, setValue, getValue, ind, GRIVEI_PATH, autostart_file


class DialogWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Dialog Example")

        self.set_border_width(6)

        grid = Gtk.Grid()
        self.add(grid)

        label_folder = Gtk.Label("Local Folder")
        folder_chooser = Gtk.FileChooser()

        label_selective = Gtk.Label("Remote Folder (leave blank for all)")
        remote_folder = Gtk.Entry()

        grid.add(label_folder)
        grid.attach(folder_chooser, 1, 0, 2, 1)
        grid.attach_next_to(label_selective, label_folder, Gtk.PositionType.BOTTOM, 1, 1)
        grid.attach_next_to(remote_folder, label_selective, Gtk.PositionType.RIGHT, 2, 1)

    def confirmSettings(self, data=None):
        setInterval(int(data.get_text()))
        setUploadSpeed(int(data.get_text()))
        setDownloadSpeed(int(data.get_text()))
        dialog.destroy()


def main():
    window = DialogWindow()
    window.show_all()
