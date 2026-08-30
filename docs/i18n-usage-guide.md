# Internationalization (i18n) Usage Guide 🌍

The Surgical Pharmacy API now supports dynamic localization (i18n) for exception messages, validation errors, and business logic responses. By default, the API communicates in **Spanish**, but fully supports **English** when requested by the client.

---

## 1. How to Request a Specific Language

The API determines your preferred language by parsing the standard HTTP `Accept-Language` header.

### Spanish (Default)

If you do not send a header, or if you request an unsupported language (like French `fr`), the API gracefully defaults to Spanish.

**cURL Example**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"invalid": "data"}'
```

**Response (422 Unprocessable Entity)**:
```json
{
  "detail": "Error de validación en los datos enviados.",
  "errors": [...]
}
```

### English

To receive error messages in English, pass `en` in the `Accept-Language` header.

**cURL Example**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
     -H "Accept-Language: en" \
     -H "Content-Type: application/json" \
     -d '{"invalid": "data"}'
```

**Response (422 Unprocessable Entity)**:
```json
{
  "detail": "Validation error in the submitted data.",
  "errors": [...]
}
```

---

## 2. Supported Domain Exceptions

The localization system natively wraps all custom domain errors. If a specific business rule is violated, the API will translate the error accordingly:

| Scenario | English (`Accept-Language: en`) | Spanish (`Accept-Language: es`) |
|----------|---------------------------------|---------------------------------|
| Item Not Found (`NotFoundError`) | `Instrument with ID 123 not found.` | `Instrument con ID 123 no encontrado.` |
| Business Logic Error (`BusinessLogicError`) | `Business rule violation: sterile mismatch` | `Violación de regla de negocio: sterile mismatch` |
| Out of Stock | `The supply 'Scalpel' is out of stock.` | `El insumo 'Scalpel' está agotado.` |

---

## 3. Developer Guide: How to Add New Translations

Translations are managed via lightweight JSON dictionaries in the `app/locales/` directory. There are no heavy compilation tools (like gettext) required.

### Step 1: Update the JSON Files

To add a new translation, simply edit the JSON files. 

**`app/locales/es.json`**:
```json
{
  "errors": {
    "insumo_agotado": "El insumo '{insumo_name}' está agotado."
  }
}
```

**`app/locales/en.json`**:
```json
{
  "errors": {
    "insumo_agotado": "The supply '{insumo_name}' is out of stock."
  }
}
```
*(Notice how you can use `{variable_name}` for dynamic string interpolation).*

### Step 2: Use the Key in Exceptions

When raising a `DomainException`, pass the dot-notated JSON key and any required interpolation variables:

```python
from app.core.domain_exceptions import DomainException

# Raise an exception dynamically!
raise DomainException(
    key="errors.insumo_agotado",
    status_code=400,
    insumo_name="Bisturí No. 4"
)
```

The global exception handler will automatically catch this, check the client's `Accept-Language` header, and return the translated string!

### Advanced: Manual Translation Lookup

If you need to translate a string inside a Router or Service directly (not via an exception), inject the `get_locale` dependency:

```python
from fastapi import APIRouter, Depends
from app.api.deps import get_locale
from app.core.i18n import i18n

router = APIRouter()

@router.get("/welcome")
async def welcome_endpoint(locale: str = Depends(get_locale)):
    message = i18n.translate("messages.welcome", locale)
    return {"message": message}
```

---

## 4. Fallback Behavior Safety

You never have to worry about the API crashing due to a missing translation:
1. **Missing Header?** Defaults to Spanish (`es`).
2. **Unsupported Header?** (e.g., `de-DE`) Defaults to Spanish (`es`).
3. **Missing Key in English JSON?** Gracefully falls back and returns the exact Spanish string.
4. **Missing Key in BOTH JSONs?** Returns the raw key (e.g., `errors.not_found`) so the client never crashes.
