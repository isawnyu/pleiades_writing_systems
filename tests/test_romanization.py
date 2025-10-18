#
# This file is part of pleiades_writing_systems
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2025 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Test the romanization module
"""

from pathlib import Path
from pleiades_writing_systems.romanization import Romanizer

test_data_path = Path(__file__).parent / "data"


class TestRomanization:
    def test_init(self):
        romanization = Romanizer()
        assert isinstance(romanization, Romanizer)
