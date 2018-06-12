import os
try:
    import pycodestyle
except ModuleNotFoundError:
    import pep8 as pycodestyle
from flake8.api import legacy as flake8
import unittest

config_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
folders = [os.path.join(config_folder, 'grive_indicator'),
           os.path.join(config_folder, 'bin'),
           os.path.join(config_folder, 'tests')]


class CodeCheck(unittest.TestCase):

    def test_pycodestyle(self):
        """Proceed a pycodestyle checking

        Note that we have a .pycodestyle config file for maximum line length tweak,
        excluding E402 and tmp files."""
        style = pycodestyle.StyleGuide(config_file=os.path.join(config_folder, '.pycodestyle'))

        # we want to use either local or system grive_indicator, but always local tests files
        results = style.check_files(folders)
        self.assertEqual(results.get_statistics(), [])

    def test_flake8(self):
        """Proceed a flake8 checking

        Note that we have a .flake8 config file for maximum line length tweak,
        excluding E402 and tmp files."""
        style_guide = flake8.get_style_guide()

        # we want to use either local or system grive_indicator, but always local tests files
        results = style_guide.check_files(folders)
        self.assertEqual(results.get_statistics('E'), [])


if __name__ == '__main__':
    unittest.main()
