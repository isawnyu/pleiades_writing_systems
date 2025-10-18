#
# This file is part of pleiades_writing_systems
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2025 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Test the romanization module
"""
import inspect
import logging
from pathlib import Path
from pleiades_writing_systems.romanization import Romanizer, RomanString
from pprint import pformat

logger = logging.getLogger("tests")
test_data_path = Path(__file__).parent / "data"


class TestRomanizerInitialization:
    def test_init(self):
        r = Romanizer()
        assert isinstance(r, Romanizer)


class TestRomanizer:
    @classmethod
    def setup_class(cls):
        logger.debug(f"starting {cls.__name__}")
        cls.romanizer = Romanizer()

    @classmethod
    def teardown_class(cls):
        del cls.romanizer
        logger.debug(f"finished {cls.__name__}")

    def setup_method(self, method):
        logger.debug(f"starting {self.__class__.__name__}::{method.__name__}")

    def teardown_method(self, method):
        logger.debug(f"finished {self.__class__.__name__}::{method.__name__}")

    def test_engines_property(self):
        engines = self.romanizer.engines
        assert isinstance(engines, list)
        assert ["python-slugify"] == engines

    def test_romanize_und(self):
        candidates = [
            ("Αθήνα", "und"),
            ("Αθήνα", "grc"),
            ("Αθήνα", "el"),
        ]
        for text, langtag in candidates:
            romanizations = self.romanizer.romanize(text, langtag)
            assert isinstance(romanizations, list)
            assert len(romanizations) == 1
            romanization = romanizations[0]
            assert isinstance(romanization, RomanString)
            assert romanization.original == text
            assert romanization.original_lang_tag == langtag
            assert romanization.romanized == "Athena"
            assert romanization.engine == "python-slugify"
