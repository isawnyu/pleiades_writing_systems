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
        assert ["python-slugify", "romanize-schizas", "romanize-manninen"] == engines

    def test_romanize(self):
        candidates = [
            (
                "Αθήνα",
                "und",
                "el",
                {"Athena", "Athina"},
                {"python-slugify", "romanize-schizas"},
            ),
            (
                "Αθήνα",
                "grc",
                "grc-Grek",
                {"Athena", "Athéna"},
                {"python-slugify", "romanize-manninen"},
            ),
            (
                "Αθήνα",
                "el",
                "el",
                {"Athena", "Athina"},
                {"python-slugify", "romanize-schizas"},
            ),
            (
                "Αθήνα",
                "grc",
                "grc-Grek",
                {"Athena", "Athéna"},
                {"python-slugify", "romanize-manninen"},
            ),
            ("Athens", "en", "en", {"Athens"}, {"python-slugify"}),
            (
                "Athens",
                "und",
                "und-Latn",
                {"Athens"},
                {"python-slugify"},
            ),  # sic more than one languages uses Latin script by default
        ]
        for i, blob in enumerate(candidates):
            text, langtag, result_langtag, result_rom, engines = blob
            romanizations = self.romanizer.romanize(text, langtag)
            assert isinstance(romanizations, list)
            for j, romanization in enumerate(romanizations):
                logger.debug(f"testing romanization result {i}:{j}")
                assert isinstance(romanization, RomanString)
                assert romanization.original == text
                assert romanization.original_lang_tag == result_langtag
                assert romanization.romanized in result_rom
                assert romanization.engine in engines

    def test_romanize_fail(self):
        candidates = [
            ("Αθήνa", "el"),  # mixed scripts
            ("Athens", "grc"),  # language mismatch
        ]
        for text, langtag in candidates:
            romanizations = self.romanizer.romanize(text, langtag)
            assert isinstance(romanizations, list)
            assert len(romanizations) == 0
