import os
import sys
try:
    import pycodestyle
except ImportError:
    import pep8 as pycodestyle
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

    def test_pyflakes(self):
        """Proceed a pyflakes checking

        Import pyflakes here so it doesn't conflict with the travis build"""

        import pyflakes
        from pyflakes import api

        # we want to use either local or system grive_indicator, but always local tests files
        reporter = pyflakes.reporter.Reporter(None, sys.stderr)
        results = api.checkRecursive(paths=folders, reporter=reporter)
        self.assertEqual(results, 0)


if __name__ == '__main__':
    unittest.main()
