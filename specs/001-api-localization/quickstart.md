# Quickstart: Testing API Localization

This guide provides runnable commands to validate that the i18n localization feature works end-to-end.

## Prerequisites

1. The FastAPI server must be running locally.
   ```bash
   uvicorn app.main:app --reload
   ```
2. The `app/locales/en.json` and `app/locales/es.json` files must be populated.

## Validation Scenarios

### Scenario 1: Verify Spanish Error (Default)

Trigger an endpoint that raises a `NotFoundError` without sending an `Accept-Language` header.

```bash
curl -X GET http://localhost:8000/api/v1/insumos/99999
```

**Expected Outcome**:
```json
{
  "detail": "Insumo con ID 99999 no encontrado."
}
```

### Scenario 2: Verify English Translation

Send the exact same request, but specify the English locale.

```bash
curl -X GET http://localhost:8000/api/v1/insumos/99999 \
     -H "Accept-Language: en"
```

**Expected Outcome**:
```json
{
  "detail": "Supply with ID 99999 not found."
}
```

### Scenario 3: Verify Missing Key Fallback

Modify the `app/locales/en.json` to intentionally delete the `errors.not_found` key, restart the server, and rerun Scenario 2.

**Expected Outcome**:
The system should gracefully fallback and return the Spanish string (from Scenario 1), ensuring the client never sees a raw key like `errors.not_found` or crashes.
