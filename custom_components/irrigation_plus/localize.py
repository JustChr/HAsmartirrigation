"""Localization utilities for Smart Irrigation integration."""

import json
import logging
from pathlib import Path

import aiofiles

from .const import LANGUAGE_FILES_DIR, SUPPORTED_LANGUAGES

_LOGGER = logging.getLogger(__name__)


async def localize(string: str, language: str) -> str:
    """Return the localized string for the given key and language.

    Attempts to load the translation from the specified language file.
    Falls back to English if the translation is not found or the language is not supported.
    If the translation cannot be found, returns the original string key.

    Args:
        string: The dot-separated key for the string to localize.
        language: The language code (e.g., 'en', 'de').

    Returns:
        The localized string, or the original string key if not found.

    """
    # try opening language file
    language = language.lower()
    translated_string = None
    main_path = Path(__file__).parent
    stringpath = string.split(".")
    try:
        # if the language is not english and the language is supported
        if language != "en" and language in SUPPORTED_LANGUAGES:
            lang_file = main_path / LANGUAGE_FILES_DIR / f"{language}.json"
            async with aiofiles.open(lang_file, encoding="utf-8") as f:
                contents = await f.read()

            data = json.loads(contents)
            translated_string = get_string_from_data(stringpath, data)
        # fallback to english in case string wasn't found
        if language == "en" or not isinstance(translated_string, str):
            en_file = main_path / LANGUAGE_FILES_DIR / "en.json"
            async with aiofiles.open(en_file, encoding="utf-8") as f:
                contents = await f.read()

            data = json.loads(contents)
            translated_string = get_string_from_data(stringpath, data)
        # if still not found, just return the string parameter
        if isinstance(translated_string, str):
            return translated_string
        return string  # noqa: TRY300
    except (OSError, json.JSONDecodeError):
        # Fall back to the KEY, never to None. Callers concatenate the result
        # straight into user-facing text (`explanation += await localize(...)`
        # in calculation.py), so returning None raised TypeError and aborted
        # that zone's whole calculation over an unreadable translation file.
        # A visible untranslated key is a far better failure than a dead zone.
        # JSONDecodeError is caught for the same reason: a truncated language
        # file (an interrupted HACS update) is exactly as recoverable.
        _LOGGER.error("Couldn't load translations language file for %s", language)
        return string


def get_string_from_data(stringpath: list[str], data: dict) -> str:
    """Retrieve a nested string value from a dictionary using a path.

    Args:
        stringpath: List of keys representing the path to the string.
        data: The dictionary to search.

    Returns:
        The string value if found, otherwise the last traversed value.

    """
    data_to_walk = data
    for p in stringpath:
        if isinstance(data_to_walk, str):
            return data_to_walk
        if p in data_to_walk:
            data_to_walk = data_to_walk[p]
    return data_to_walk
