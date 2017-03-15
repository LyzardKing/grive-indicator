#!/usr/bin/env python3

import os
import gi
import re
import shutil
import site
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from contextlib import suppress
import json
import subprocess
from grive_indicator.tools import getIcon, setValue, getValue, ind, GRIVEI_PATH, autostart_file


class SettingsWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Settings")

        self.set_border_width(6)

        grid = Gtk.Grid()
        self.add(grid)

        label_timer = Gtk.Label("Sync timer")
        timer_entry = Gtk.Entry()
        timer_entry.set_text(str(getValue('time')))

        label_theme = Gtk.Label("Dark Theme")
        theme_swith = Gtk.Switch()
        theme_swith.set_active(True)
        theme_swith.connect('notify::active', self.on_dark_theme_activate)

        label_startup = Gtk.Label("Enable  on Startup")
        startup_swith = Gtk.Switch()
        startup_swith.set_active(os.path.isfile(autostart_file))
        startup_swith.connect('notify::active', self.on_startup_active)

        label_up_speed = Gtk.Label("Limit Upload Speed")
        upload_speed = Gtk.Entry()
        tmp = str(getValue('upload_speed'))
        upload_speed.set_text(tmp if tmp is not None else '')

        label_down_speed = Gtk.Label("Limit Download Speed")
        download_speed = Gtk.Entry()
        tmp = str(getValue('download_speed'))
        download_speed.set_text(tmp if tmp is not None else '')

        confirm_button = Gtk.Button('Ok')
        confirm_button.connect('clicked',
                               self.confirmSettings,
                               timer_entry.get_text(),
                               upload_speed.get_text(),
                               download_speed.get_text())

        grid.add(label_timer)
        grid.attach(timer_entry, 1, 0, 2, 1)
        grid.attach_next_to(label_theme, label_timer, Gtk.PositionType.BOTTOM, 1, 1)
        grid.attach_next_to(theme_swith, label_theme, Gtk.PositionType.RIGHT, 2, 1)
        grid.attach_next_to(label_startup, label_theme, Gtk.PositionType.BOTTOM, 1, 1)
        grid.attach_next_to(startup_swith, label_startup, Gtk.PositionType.RIGHT, 2, 1)
        grid.attach_next_to(label_up_speed, label_startup, Gtk.PositionType.BOTTOM, 1, 1)
        grid.attach_next_to(upload_speed, label_up_speed, Gtk.PositionType.RIGHT, 2, 1)
        grid.attach_next_to(label_down_speed, label_up_speed, Gtk.PositionType.BOTTOM, 1, 1)
        grid.attach_next_to(download_speed, label_down_speed, Gtk.PositionType.RIGHT, 2, 1)
        grid.attach_next_to(download_speed, confirm_button, Gtk.PositionType.BOTTOM, 1, 1)

    def on_dark_theme_activate(self, switch, gparam):
        if switch.get_active():
            setDarkTheme()
        else:
            setLightTheme()

    def on_startup_active(self, switch, gparam):
        enableStartup(switch.get_active())

    def confirmSettings(self, timer=None, upload_speed=None, download_speed=None):
        setInterval(int(timer))
        with suppress(ValueError):
            setUploadSpeed(int(upload_speed))
        with suppress(ValueError):
            setDownloadSpeed(int(download_speed))
        self.destroy()


def setDownloadSpeed(value):
    if value is not None and value != getValue('download_speed'):
        setValue('download_speed', value)


def setUploadSpeed(value):
    if value is not None and value != getValue('upload_speed'):
        setValue('upload_speed', value)


def setInterval(value):
    if value is not None and value != getValue('time'):
        setValue("time", value)


def enableStartup(is_active):
    if is_active:
        if not os.path.isfile(autostart_file):
            shutil.copyfile(src=os.path.join(GRIVEI_PATH, "data", 'grive-indicator.desktop'),
                            dst=os.path.join(os.path.expanduser('~'), '.config',
                                             'autostart', 'grive-indicator.desktop'))
            with open(os.path.join(os.path.expanduser('~'), '.config', 'autostart',
                                   'grive-indicator.desktop'), 'r') as f:
                txt = f.read()
                print(GRIVEI_PATH)
                if os.path.dirname(GRIVEI_PATH) in site.getsitepackages():
                    txt = re.sub(r"GRIVEI_PATH/", '', txt)
                else:
                    txt = re.sub(r"GRIVEI_PATH/", '{}/'.format(os.path.join(os.path.dirname(GRIVEI_PATH), 'bin')), txt)
            with open(os.path.join(os.path.expanduser('~'), '.config', 'autostart',
                                   'grive-indicator.desktop'), 'w') as f:
                f.write(txt)
    else:
        if os.path.exists(autostart_file):
            os.remove(autostart_file)


def setDarkTheme():
    setValue("style", "dark")
    ind.set_icon_full(os.path.join(GRIVEI_PATH, "data", getIcon()), "grive-indicator-dark")


def setLightTheme():
    setValue("style", "light")
    ind.set_icon_full(os.path.join(GRIVEI_PATH, "data", getIcon()), "grive-indicator-light")


def main():
    window = SettingsWindow()
    window.show_all()
