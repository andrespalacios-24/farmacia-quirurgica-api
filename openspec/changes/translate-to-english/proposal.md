## Why

The project's code, including comments, internal variables, function names, and API contracts (endpoints and JSON schemas) is currently in Spanish. We need to translate these elements into English to standardize the language used across the codebase, which makes it more accessible to international developers. The database schemas/models will remain in Spanish to avoid breaking existing queries or requiring database migrations.

## What Changes

- **API Routes**: Update endpoint paths from Spanish to English (e.g., `/insumos` to `/supplies`, `/pacientes` to `/patients`). **BREAKING**
- **JSON Schemas**: Translate Pydantic models (request and response payloads) fields to English. **BREAKING**
- **Internal Code**: Translate function names, variable names, comments, docstrings, and error messages to English.
- **Database Mapping**: Explicitly map the new English attributes to the existing Spanish database columns using SQLAlchemy configurations to ensure backwards compatibility with the existing database.

## Capabilities

### New Capabilities
- `api-contracts`: Defines the new English-based API endpoints and JSON request/response structures.

### Modified Capabilities
<!-- No existing capabilities to modify as the specs folder was empty -->

## Impact

- **API Clients**: External systems consuming the API will need to be updated to use the new English endpoints and JSON structures.
- **Codebase**: All Python files in the `/app` directory will undergo significant renaming.
- **Database**: Unaffected. The SQLAlchemy models will map the new English field names to the legacy Spanish column names.
