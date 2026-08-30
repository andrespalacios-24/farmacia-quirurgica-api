# Feature Specification: API Localization (i18n) Support

**Feature Branch**: `[001-api-localization]`

**Created**: 2026-08-29

**Status**: Draft

**Input**: User description: "i need to add locales to all expception messages and meesages rendered in api so we support en and spanish languages."

## Clarifications

### Session 2026-08-29

- Q: Which implementation strategy should we adopt to store and load translations while preserving FastAPI's async performance? → A: Simple JSON dictionary files loaded in memory
- Q: If a translation key is missing in the requested language, what should the API return? → A: Fallback to the default language string (Spanish)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Receive error messages in Spanish (Priority: P1)

As an API client or surgical technologist using a Spanish-configured interface, I want to receive all exception and validation errors in Spanish, so that I can easily understand what went wrong without manual translation.

**Why this priority**: Spanish is the primary language of the surgical context defined in the project, so it must work flawlessly.

**Independent Test**: Can be fully tested by sending an API request that deliberately causes a domain exception while providing the `Accept-Language: es` header, and verifying the response payload is in Spanish.

**Acceptance Scenarios**:

1. **Given** the API is configured with multiple locales, **When** a client sends a request that triggers a business logic error with `Accept-Language: es`, **Then** the JSON response detail contains the Spanish translation of the error.
2. **Given** the API is configured with multiple locales, **When** a client sends a request that triggers a Pydantic validation error with `Accept-Language: es`, **Then** the validation error details are rendered in Spanish.

---

### User Story 2 - Receive error messages in English (Priority: P1)

As an API client using an English-configured interface, I want to receive all exception and validation errors in English, so that non-Spanish speaking integrations can parse and understand the API responses.

**Why this priority**: The explicit goal of the feature is to support both English and Spanish cleanly.

**Independent Test**: Can be fully tested by sending the exact same failing request as US1, but altering the header to `Accept-Language: en`, and verifying the payload is in English.

**Acceptance Scenarios**:

1. **Given** the API is configured with multiple locales, **When** a client sends a request that triggers a business logic error with `Accept-Language: en`, **Then** the JSON response detail contains the English translation of the error.

---

### User Story 3 - Fallback to Default Language (Priority: P2)

As a generic API client that does not specify a language, I want the API to gracefully fall back to a default language (Spanish) rather than failing, so that my requests still work without modification.

**Why this priority**: Prevents breaking changes for existing clients that aren't aware of the new localization feature.

**Independent Test**: Can be fully tested by omitting the `Accept-Language` header and verifying the response matches the default project language.

**Acceptance Scenarios**:

1. **Given** a client request omitting the `Accept-Language` header, **When** an error occurs, **Then** the response is served in the default fallback language (Spanish).
2. **Given** a client request with an unsupported locale (e.g., `Accept-Language: fr`), **When** an error occurs, **Then** the response is served in the default fallback language (Spanish).

---

### Edge Cases

- **Missing Translation Key**: If a specific translation key is missing in the requested language (e.g., English), the system will automatically fallback to the string defined in the default language (Spanish).
- How does the system handle complex string formatting inside error messages (e.g., "Instrument {name} not found") across different languages?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST determine the requested locale from the standard `Accept-Language` HTTP header.
- **FR-002**: System MUST translate all Domain Exceptions (e.g., NotFoundError, BusinessLogicError) into the determined locale before returning the HTTP response.
- **FR-003**: System MUST translate standard FastAPI/Pydantic validation errors (`RequestValidationError`) into the determined locale.
- **FR-004**: System MUST translate informational API responses (e.g., "Welcome to the API") into the determined locale.
- **FR-005**: System MUST fall back to Spanish if the requested locale is missing, invalid, or unsupported.
- **FR-006**: System MUST fall back to the Spanish translation string if a specific translation key is missing in the valid, requested locale.
- **FR-007**: System MUST support dynamic variable interpolation within translated strings (e.g., inserting IDs or entity names into the localized message).

### Key Entities

- **Locale Registry**: A dictionary or registry of translation keys and their corresponding strings in supported languages (`en`, `es`).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of the API's global exception handlers render localized text based on client headers.
- **SC-002**: Adding a new language in the future requires only adding a new translation dictionary/file, without modifying core business logic.
- **SC-003**: Clients experience 0 millisecond perceivable latency overhead from the translation layer.

## Assumptions

- The `Accept-Language` HTTP header will be the primary mechanism for determining the client's locale.
- Spanish (`es`) will be the default fallback language given the project's original language context.
- Translation strings will be managed locally using simple JSON dictionary files loaded into memory at startup, avoiding external third-party services and blocking I/O during requests.
