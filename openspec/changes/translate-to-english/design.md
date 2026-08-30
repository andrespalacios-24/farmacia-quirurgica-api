## Context

The codebase is currently in Spanish, but we need to translate all internal code, Pydantic schemas, and API endpoints to English. See proposal.md for motivation. The critical constraint is that the underlying PostgreSQL database schemas and table names must remain in their original Spanish language to avoid breaking existing infrastructure.

## Goals / Non-Goals

**Goals:**
- Provide a systematic approach for translating Python code in the `app` module.
- Detail how to maintain backward compatibility with the Spanish database while using English models in SQLAlchemy.

**Non-Goals:**
- Creating database migrations (Alembic) to rename tables or columns.
- Modifying the actual PostgreSQL database schema.

## Decisions

### Database Model Mapping
**Decision:** We will use SQLAlchemy's explicit column mapping to bind English class attributes to Spanish database column names.
**Rationale:** This allows the rest of the application (routers, Pydantic schemas, services) to work purely with English attributes without requiring a database migration. For example, `id_paciente` becomes `patient_id = mapped_column("id_paciente", ...)`.
**Alternatives:** 
- Translating the database schemas via Alembic (Rejected: User explicitly requested not to touch database names as it might break existing integrations).

### API Contract Translation
**Decision:** We will rename the FastAPI route paths and the keys in Pydantic models.
**Rationale:** Standardizing the API contracts to English ensures a consistent developer experience for international consumers. This will be a breaking change for existing clients.
**Alternatives:** 
- Keeping Spanish API routes and only translating internal variables (Rejected: User requested to translate API payloads and routes as well).

## Risks / Trade-offs

- **Risk**: Missed mappings could cause SQLAlchemy `KeyError` or missing column exceptions.
  **Mitigation**: Run existing test suites (if any) and manually test critical endpoints after the translation.
- **Risk**: External clients breaking due to the endpoint and JSON payload changes.
  **Mitigation**: The breaking changes are acknowledged. The team must notify any API consumers to update their integrations.
