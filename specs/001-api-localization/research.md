# Research & Technical Decisions: API Localization

## 1. Localization Library vs Custom Lightweight Loader

**Context**: The user requested to "use a recommended library for translations in fastapi or do whats best". The primary ambiguity is whether to adopt a robust external library like `fastapi-babel` or build a lightweight custom JSON loader.

**Decision**: Implement a **Custom Lightweight JSON Loader** (`app/core/i18n.py`).

**Rationale**:
- **Simplicity and Build Process**: Libraries like `fastapi-babel` rely on GNU gettext (`.po` and `.mo` files), which require a compilation step (`pybabel compile`) every time a translation changes. A custom JSON loader reads standard `.json` files into a Python dictionary at application startup, requiring no build tools. This is vastly easier for clinical and non-technical stakeholders to maintain.
- **Performance**: A native Python dictionary lookup (`translations.get(locale, {}).get(key)`) is an $O(1)$ operation in memory and introduces literally 0ms of overhead.
- **Dependency Minimization**: Avoids adding `Babel` and `fastapi-babel` to the dependency tree, keeping the microservice lean.
- **Scope Alignment**: For an API with 100-500 error messages (no complex pluralization rules or frontend HTML rendering needed), gettext is overkill.

**Alternatives Considered**:
- `fastapi-babel`: Great for large monoliths or full-stack Jinja2 templates, but heavy for a strict JSON API.
- Python's built-in `gettext` module: Still requires `.mo` compiled files.

## 2. Header Extraction Pattern

**Context**: How to intercept and parse the `Accept-Language` header globally without bloating every router.

**Decision**: Use a FastAPI Dependency (`Depends(get_locale)`) for normal endpoints, and direct `request.headers.get("accept-language")` parsing inside the global Exception Handlers.

**Rationale**:
- Fits the Constitution's strict rule on Dependency Injection.
- Ensures the global exception handler can safely determine the language even if the request fails before reaching the router's dependencies.
