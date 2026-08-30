# Interface Contract: I18nService

The localization feature exposes an internal Python interface for the rest of the application (routers and exception handlers) to translate keys.

## `app.core.i18n.translate`

```python
def translate(key: str, locale: str, **kwargs) -> str:
    """
    Translates a given key into the requested locale.
    
    Args:
        key (str): The dot-notated key to translate (e.g., "errors.not_found").
        locale (str): The ISO 639-1 language code (e.g., "en", "es").
        **kwargs: Keyword arguments for dynamic string interpolation.
        
    Returns:
        str: The translated string, or the fallback string if missing.
    """
    pass
```

## `app.api.deps.get_locale`

```python
from fastapi import Header

async def get_locale(accept_language: str | None = Header(default=None)) -> str:
    """
    FastAPI dependency to extract and sanitize the requested language.
    Returns "es" by default if the header is missing or unsupported.
    """
    pass
```
