#
# This file is part of pleiades_writing_systems
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2025 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
romanization: create romanized (Latin script) versions of strings in other scripts
"""
from functools import lru_cache
import langcodes
import logging
from pprint import pformat
from romanize import romanize as romanize_schizas
import slugify as python_slugify
from datetime import timedelta
import unicodedata
from webiquette.webi import Webi


class RomanizationUnsupportedLanguageError(Exception):
    """
    Exception raised when attempting to romanize text in an unsupported language/script.
    """

    def __init__(self, message: str):
        super().__init__(message)


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

    def __str__(self):
        return f"RomanString({self.romanized} from {self.original} ({self.original_lang_tag}) via {self.engine})"

    def __repr__(self):
        return str(self)


class Romanizer:
    """
    A class to handle romanization of various writing systems.
    """

    def __init__(self):
        # Initialize any necessary data structures or mappings here
        self._engines = {
            "python-slugify": self._romanize_with_python_slugify,  # "python-slugify" by Val Neekman: https://pypi.org/project/python-slugify/
            "romanize-schizas": self._romanize_with_romanize_schizas,  # "romanize" by George Schizas: https://pypi.org/project/Romanize/
        }
        self._script_detector = ScriptDetector()

    @property
    def engines(self):
        """
        Return the available romanization engines.
        """
        return list(self._engines.keys())

    @lru_cache(maxsize=5000)
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

        logger.debug(f"lang_tags as input: {lang_tags}")
        # validate and standardize the lang tag
        if not langcodes.tag_is_valid(lang_tags):
            raise ValueError(
                f"Invalid BCP 47 language tag(s) '{lang_tags}' for text '{text}'"
            )
        standardized_lang_tag = langcodes.standardize_tag(lang_tags)
        if standardized_lang_tag != lang_tags:
            logger.warning(
                f"Non-standard BCP 47 language tag '{lang_tags}' replaced with standardized tag '{standardized_lang_tag}'"
            )
            lang_tags = standardized_lang_tag
        logger.debug(f"standardized lang_tags: {lang_tags}")

        # detect the script(s) used in the input text
        actual_scripts = self._script_detector.detect_scripts(text)
        if len(actual_scripts) != 1:
            logger.error(
                f"Detected {len(actual_scripts)} scripts in text '{text}'; skipping romanization"
            )
            return []
        source_script = actual_scripts[0]
        logger.debug(f"source_script: {source_script}")

        # try to guess the language tag on the basis of script if undefined
        if lang_tags == "und":
            candidates = self._script_detector.languages_by_script.get(
                source_script, set()
            )
            if len(candidates) == 1:
                lang_tags = list(candidates)[0]
                logger.debug(
                    f"Guessed language tag '{lang_tags}' for script '{source_script}'"
                )

        # if we think we know the real language tag, check that the script matches expectations
        if lang_tags != "und":
            expected_script = None
            lang = langcodes.Language.get(lang_tags)
            if lang.language == "grc":
                expected_script = "Grek"  # not included in langcodes default scripts
            else:
                expected_script = lang.script
            if source_script != expected_script and expected_script is not None:
                logger.error(
                    f"Detected script '{source_script}' in text '{text}' does not match expected script '{expected_script}' for langtag '{lang_tags}; skipping romanization'"
                )
                return []
            source_language = lang.language
        else:
            source_language = "und"
        logger.debug(f"source_language: {source_language}")

        # perform romanization using all appropriate engines
        romanizations = list()
        if lang_tags.startswith("und"):
            # use only python-slugify for undefined language tags
            romanizations = self._engines["python-slugify"](
                text, lang_subtag=source_language, script_subtag=source_script
            )
        else:
            # use all available engines for defined language tags
            for engine_name, engine_func in self._engines.items():
                try:
                    romanized_forms = engine_func(
                        text, lang_subtag=source_language, script_subtag=source_script
                    )
                except RomanizationUnsupportedLanguageError as err:
                    logger.error(
                        f"Romanization engine '{engine_name}' failed for text '{text}' with langtag '{lang_tags}' (source_language: '{source_language}', source_script: '{source_script}'): {err}"
                    )
                else:
                    romanizations.extend(romanized_forms)
        return romanizations

    @lru_cache(maxsize=5000)
    def _romanize_with_python_slugify(
        self, text: str, lang_subtag: str, script_subtag: str
    ) -> list[RomanString]:
        """
        Romanize the input text using the python-slugify engine.

        Args:
            text (str): The input text in its original script.
            lang_subtag (str): IANA language subtag for reporting.
            script_subtag (str): IANA script subtag for reporting.
        Returns:
            list[RomanString]: A list containing one or more romanized forms of the input "text" string.
        Notes:
            The python slugify engine is used to produce one and only one romanized form using its
            internal algorithm. No information about language or script is passed to the engine.
        """

        return [
            RomanString(
                original_text=text,
                original_lang_tag=langcodes.standardize_tag(
                    f"{lang_subtag}-{script_subtag}"
                ),
                romanized_form=python_slugify.slugify(
                    text, separator=" ", lowercase=False
                ),
                engine="python-slugify",
            )
        ]

    @lru_cache(maxsize=5000)
    def _romanize_with_romanize_schizas(
        self, text: str, lang_subtag: str, script_subtag: str
    ) -> list[RomanString]:
        """
        Romanize the input text using the romanize engine.

        Args:
            text (str): The input text in its original script.
            lang_subtag (str): IANA language subtag for reporting.
            script_subtag (str): IANA script subtag for reporting.
        Returns:
            list[RomanString]: A list containing one or more romanized forms of the input "text" string.
        Notes:
            The romanize engine is used to produce one and only one romanized form using its
            internal algorithm. No information about language or script is passed to the engine.
        """
        langtags = langcodes.standardize_tag(f"{lang_subtag}-{script_subtag}")
        supported_lang_subtags = {"el"}
        supported_script_subtags = {"Grek"}
        if (
            lang_subtag in supported_lang_subtags
            and script_subtag in supported_script_subtags
        ):
            romanized_text = romanize_schizas(text)
            return [
                RomanString(
                    original_text=text,
                    original_lang_tag=langtags,
                    romanized_form=romanized_text,
                    engine="romanize-schizas",
                )
            ]
        else:
            raise RomanizationUnsupportedLanguageError(
                f"Unsupported language/script for romanize engine: {langtags}"
            )
        return []


class ScriptDetector:
    """
    A class to detect the script(s) used in a given text.
    """

    def __init__(self):
        headers = {
            "User-Agent": "pleiades_writing_systems Romanizer ScriptDetector/https://pleiades.stoa.org, pleiades.admin@nyu.edu",
            "From": "pleiades.admin@nyu.edu",
        }
        cache_max_age = timedelta(days=30)
        webi = Webi(
            netloc="iana.org",
            headers=headers,
            expire_after=cache_max_age,
            respect_robots_txt=False,
        )
        r = webi.get(
            "https://www.iana.org/assignments/language-subtag-registry/language-subtag-registry"
        )
        self._registry = r.text
        self.scripts_by_description = dict()
        self.scripts_by_subtag = dict()
        self.languages_by_script = dict()
        self._parse_registry()

    @lru_cache(maxsize=5000)
    def detect_scripts(self, text: str) -> list[str]:  # type: ignore
        """
        Detect the script(s) used in the input text.

        Args:
            text (str): The input text in its original script.
        Returns:
            set[str]: A set of script codes detected in the input text.
        Notes:
            This method uses Unicode character properties to identify the scripts present in the text.
        """
        chars = set(text)
        scriptnames = {unicodedata.name(c).split(" ")[0] for c in chars if c.isalpha()}
        logger = logging.getLogger(__name__)
        logger.debug(f"script names: {pformat(scriptnames)}")
        script_tags = {
            self.scripts_by_description.get(name.title()) for name in scriptnames
        }
        return list(script_tags)  # type: ignore

    def _parse_registry(self):
        """
        Parse the IANA Language Subtag Registry to extract script subtags.
        """
        entries = self._registry.split("%%\n")
        for entry in entries:
            lines = entry.strip().split("\n")
            continuation_lines = [l for l in lines if l.startswith("  ")]
            if continuation_lines:
                new_lines = []
                for line in lines:
                    if line.startswith("  "):
                        " ".join((new_lines[-1], line[2:]))
                    else:
                        new_lines.append(line)
                lines = new_lines
            if lines[0] == "Type: language":
                subtag = ""
                script = ""
                for line in lines[1:]:
                    try:
                        prefix, suffix = line.split(": ", 1)
                    except ValueError as err:
                        err.add_note(f"while parsing language entry: {entry}")
                        raise
                    if prefix == "Subtag":
                        if subtag:
                            raise ValueError(
                                f"Multiple Subtag fields in single language entry: {entry}"
                            )
                        subtag = line.split(": ", 1)[1].strip()
                    elif prefix == "Suppress-Script":
                        if script:
                            raise ValueError(
                                f"Multiple Script fields in single language entry: {entry}"
                            )
                        script = line.split(": ", 1)[1].strip()
                    elif prefix in {
                        "Added",
                        "Comments",
                        "Description",
                        "Scope",
                        "Macrolanguage",
                        "Deprecated",
                        "Preferred-Value",
                    }:
                        pass
                    else:
                        raise ValueError(
                            f"Unexpected field '{prefix}' in language entry: {entry}"
                        )
                if subtag and script:
                    try:
                        self.languages_by_script[script]
                    except KeyError:
                        self.languages_by_script[script] = set()
                    self.languages_by_script[script].add(subtag)
            elif lines[0] == "Type: script":
                subtag = ""
                descriptions = set()
                for line in lines[1:]:
                    try:
                        prefix, suffix = line.split(": ", 1)
                    except ValueError as err:
                        err.add_note(f"while parsing script entry: {entry}")
                        raise
                    if prefix == "Subtag":
                        if subtag:
                            raise ValueError(
                                f"Multiple Subtag fields in single script entry: {entry}"
                            )
                        subtag = line.split(": ", 1)[1].strip()
                    elif prefix == "Description":
                        descriptions.add(suffix.strip())
                    elif prefix in {"Added", "Comments"}:
                        pass
                    else:
                        raise ValueError(
                            f"Unexpected field '{prefix}' in script entry: {entry}"
                        )
                if subtag and descriptions:
                    for description in descriptions:
                        try:
                            self.scripts_by_description[description]
                        except KeyError:
                            self.scripts_by_description[description] = subtag
                        else:
                            raise ValueError(
                                f"Duplicate script description '{description}' for subtags '{self.scripts_by_description[description]}' and '{subtag}'"
                            )
                    try:
                        self.scripts_by_subtag[subtag]
                    except KeyError:
                        self.scripts_by_subtag[subtag] = descriptions
                    else:
                        raise ValueError(
                            f"Duplicate script subtag '{subtag}' for descriptions '{self.scripts_by_subtag[subtag]}' and '{descriptions}'"
                        )
