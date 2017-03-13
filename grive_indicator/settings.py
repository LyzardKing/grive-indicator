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

        grid.add(label_timer)
        grid.attach(timer_entry, 1, 0, 2, 1)
        grid.attach_next_to(label_theme, label_timer, Gtk.PositionType.BOTTOM, 1, 1)
        grid.attach_next_to(theme_swith, label_theme, Gtk.PositionType.RIGHT, 2, 1)
        grid.attach_next_to(label_startup, label_theme, Gtk.PositionType.BOTTOM, 1, 1)
        grid.attach_next_to(startup_swith, label_startup, Gtk.PositionType.RIGHT, 2, 1)

    def on_dark_theme_activate(self, switch, gparam):
        if switch.get_active():
            setDarkTheme()
        else:
            setLightTheme()
    def on_startup_active(self, switch, gparam):
        enableStartup(switch.get_active())

    def confirmSettings(self, data=None):
        setInterval(int(data.get_text()))
        dialog.destroy()

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
    window = DialogWindow()
    window.show_all()
