#
# This file is part of pleiades_writing_systems
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2025 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
romanization: create romanized (Latin script) versions of strings in other scripts
"""
import slugify as python_slugify


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
            "python-slugify": self._romanize_with_python_slugify,  # Placeholder for actual romanization engine
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
