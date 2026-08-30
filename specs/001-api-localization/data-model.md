# Data Model: API Localization

## 1. Translation Dictionary (JSON)

The translation data will not reside in a SQL database. Instead, it will be stored as static JSON files in the `app/locales/` directory.

### File Structure
- `app/locales/es.json` (Default fallback)
- `app/locales/en.json`

### Schema (Key-Value)
The JSON files will follow a flat or slightly nested key-value structure mapping domain exception keys to their translated strings.

```json
{
  "errors": {
    "not_found": "{entity_name} with ID {entity_id} not found.",
    "business_logic": "Business rule violation: {detail}",
    "insumo_agotado": "The supply '{insumo_name}' is out of stock."
  },
  "messages": {
    "welcome": "Welcome to the Surgical Pharmacy API"
  }
}
```

## 2. In-Memory State (`I18nService`)

During application startup, these JSON files will be loaded into a singleton Python dictionary.

```python
class I18nService:
    translations: dict[str, dict] = {
        "es": {...},
        "en": {...}
    }
    default_locale: str = "es"
```

## Validation Rules
- If a locale file fails to parse during startup, the application should raise a startup exception (fail-fast).
- Missing keys during runtime will fallback to the `default_locale` dictionary. If still missing, the raw key will be returned.
