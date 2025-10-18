#
# This file is part of pleiades_writing_systems
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2025 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
romanization: create romanized (Latin script) versions of strings in other scripts
"""
import langcodes
import logging
import slugify as python_slugify
from romanize import romanize as romanize_engine


class RomanString:
    """
    A class to represent romanized text along with its metadata.
    """

    def __init__(
        self,
        original_text: str,
        original_lang_tag: str,
        romanized_form: str,
        engine: str,
    ):
        self.original = original_text
        self.original_lang_tag = original_lang_tag
        self.romanized = romanized_form
        self.engine = engine


class Romanizer:
    """
    A class to handle romanization of various writing systems.
    """

    def __init__(self):
        # Initialize any necessary data structures or mappings here
        self._engines = {
            "python-slugify": self._romanize_with_python_slugify,  # by Val Neekman: https://pypi.org/project/python-slugify/
            # "romanize": None,  # by George Schizas: https://pypi.org/project/Romanize/
        }

    @property
    def engines(self):
        """
        Return the available romanization engines.
        """
        return list(self._engines.keys())

    def romanize(self, text: str, lang_tags: str = "und") -> list[RomanString]:
        """
        Romanize the input text from its original script to Latin script.

        Args:
            text (str): The input text in its original script.
            langtags (str): IANA language tags to guide romanization (default is "und" for undefined).
        Returns:
            list[RomanString]: A list containing one or more romanized forms of the input "text" string.
        Notes:
            This method applies all available romanization engines to the input text and
            aggregates the results.
        """
        logger = logging.getLogger(__name__)
        if lang_tags != "und":
            if not langcodes.tag_is_valid(lang_tags):
                raise ValueError(
                    f"Invalid BCP 47 language tag(s) '{lang_tags}' for text '{text}'"
                )
            standardized_lang_tag = langcodes.standardize_tag(lang_tags)
            if standardized_lang_tag != lang_tags:
                logger.warning(
                    f"Non-standard BCP 47 language tag '{lang_tags}' replaced with standardized tag '{standardized_lang_tag}'"
                )
            lang = langcodes.Language.get(standardized_lang_tag)
            expected_script = lang.script
            logger.debug(
                f"Expected script '{expected_script}' for lang tag '{standardized_lang_tag}'"
            )

        romanizations = list()
        for engine_func in self._engines.values():
            romanized_forms = engine_func(text, lang_tags)
            romanizations.extend(romanized_forms)
        return romanizations

    def _romanize_with_python_slugify(
        self, text: str, lang_tags: str = "und"
    ) -> list[RomanString]:
        """
        Romanize the input text using the python-slugify engine.

        Args:
            text (str): The input text in its original script.
            langtags (str): IANA language tags to guide romanization (default is "und" for undefined).
        Returns:
            list[RomanString]: A list containing one or more romanized forms of the input "text" string.
        Notes:
            The python slugify engine is used to produce one and only one romanized form using its
            internal algorithm. No information about language or script is passed to the engine.
        """
        return [
            RomanString(
                original_text=text,
                original_lang_tag=lang_tags,
                romanized_form=python_slugify.slugify(
                    text, separator=" ", lowercase=False
                ),
                engine="python-slugify",
            )
        ]

    def _romanize_with_romanize_engine(
        self, text: str, lang_tags: str = "und"
    ) -> list[RomanString]:
        """
        Romanize the input text using the romanize engine.

        Args:
            text (str): The input text in its original script.
            langtags (str): IANA language tags to guide romanization (default is "und" for undefined).
        Returns:
            list[RomanString]: A list containing one or more romanized forms of the input "text" string.
        Notes:
            The romanize engine is used to produce one and only one romanized form using its
            internal algorithm. No information about language or script is passed to the engine.
        """
        supported_lang_subtags = {"grc", "el", "und"}
        supported_script_subtags = {"Grek"}

        return []
