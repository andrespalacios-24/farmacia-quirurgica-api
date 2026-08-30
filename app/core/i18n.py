import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger("farmacia-quirurgica.i18n")

class I18nService:
    _translations: dict[str, dict] = {}
    default_locale: str = "es"
    _is_loaded: bool = False

    @classmethod
    def load_translations(cls, locales_dir: Path = Path("app/locales")):
        if cls._is_loaded:
            return
            
        try:
            for filepath in locales_dir.glob("*.json"):
                locale = filepath.stem
                with open(filepath, "r", encoding="utf-8") as f:
                    cls._translations[locale] = json.load(f)
            cls._is_loaded = True
            logger.info(f"Translations loaded for locales: {list(cls._translations.keys())}")
        except Exception as e:
            logger.error(f"Failed to load translations: {e}")
            raise

    @classmethod
    def translate(cls, key: str, locale: str = None, **kwargs: Any) -> str:
        if not cls._is_loaded:
            cls.load_translations()
            
        locale = locale or cls.default_locale
        
        # Try to get translation in requested locale
        translation_dict = cls._translations.get(locale, {})
        
        # Split key by dot for nested dictionaries
        parts = key.split(".")
        current = translation_dict
        
        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            else:
                current = None
                break
                
        # Fallback to default locale if missing
        if current is None and locale != cls.default_locale:
            default_dict = cls._translations.get(cls.default_locale, {})
            current_fallback = default_dict
            for part in parts:
                if isinstance(current_fallback, dict):
                    current_fallback = current_fallback.get(part)
                else:
                    current_fallback = None
                    break
            current = current_fallback
            
        # If still missing, return the raw key
        if current is None or not isinstance(current, str):
            return key
            
        # Interpolate variables
        try:
            return current.format(**kwargs)
        except KeyError:
            # If interpolation fails due to missing kwargs, return raw string
            return current

def get_locale_from_header(accept_language: str | None) -> str:
    """Helper to parse Accept-Language header."""
    if not accept_language:
        return I18nService.default_locale
    primary_lang = accept_language.split(",")[0].split("-")[0].strip().lower()
    if primary_lang in ["es", "en"]:
        return primary_lang
    return I18nService.default_locale

# Initialize instance methods globally or just use classmethods
i18n = I18nService
