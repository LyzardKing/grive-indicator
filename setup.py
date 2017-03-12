from distutils.core import setup

data = ["data/*"]

setup(name = 'grive-indicator',
      version = '1.0',
      packages = ['grive_indicator'],
      package_data = {'grive_indicator': data},
      scripts = ['bin/grive-indicator']
      )
