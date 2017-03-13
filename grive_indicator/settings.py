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

class Handler:
    def onDeleteWindow(self, *args):
        Gtk.main_quit(*args)
    def confirmSettings(self, data=None):
        setInterval(int(data.get_text()))
    def on_dark_theme_activate(self, dark_theme, gparam):
        if dark_theme.get_active():
            setDarkTheme()
        else:
            setLightTheme()
    def on_startup_active(self, startup, gparam):
        enableStartup(startup.get_active())

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
    builder = Gtk.Builder()
    builder.add_from_file("resources/settings.glade")
    builder.connect_signals(Handler())

    window = builder.get_object("settings_dialog")
    timer_entry = builder.get_object("sync_interval")
    timer_entry.set_text(str(getValue('time')))
    window.show_all()
    Gtk.main()
