from tests import folders
from unittest import TestCase
from flake8.api import legacy as flake8


class StyleCheck(TestCase):

    def test_pyflakes(self):
        """Proceed a pyflakes checking"""

        style_guide = flake8.get_style_guide(ignore=['E402', 'E408', 'E501', 'W605'])
        report = style_guide.check_files(folders)
        assert report.get_statistics('E') == [], 'Flake8 found violations'
