from distutils.core import setup

data = ["data/*"]

setup(name='grive-indicator',
      version='1.0',
      packages=['grive_indicator'],
      package_data={'grive_indicator': data},
      data_files=[('/usr/share/applications', ['grive-indicator.desktop']),
                  ('/usr/share/pixmaps/', ['web-google-drive.svg'])],
      scripts=['bin/grive-indicator']
      )
