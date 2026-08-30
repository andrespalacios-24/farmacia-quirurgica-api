---
description: "Task list for API Localization (i18n) Support implementation"
---

# Tasks: API Localization (i18n) Support

**Input**: Design documents from `specs/001-api-localization/`

**Prerequisites**: plan.md, spec.md, data-model.md, contracts/i18n_interface.md, research.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Exact file paths are included in descriptions.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure for locales.

- [X] T001 [P] Create the `app/locales` directory structure

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented.
**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T002 Implement `I18nService` class and dictionary loader in `app/core/i18n.py`
- [X] T003 Implement the `get_locale` dependency extractor in `app/api/deps.py`

**Checkpoint**: Foundation ready - user story implementation can now begin.

---

## Phase 3: User Story 1 - Receive error messages in Spanish (Priority: P1) 🎯 MVP

**Goal**: As an API client using a Spanish-configured interface, I want to receive all exception and validation errors in Spanish.

**Independent Test**: Trigger a domain error and verify the JSON response contains the Spanish text.

### Implementation for User Story 1

- [X] T004 [P] [US1] Create the initial Spanish translation file in `app/locales/es.json`
- [X] T005 [US1] Update `domain_exception_handler` in `app/core/exceptions.py` to use `I18nService.translate`
- [X] T006 [US1] Update `validation_handler` in `app/core/exceptions.py` to use `I18nService.translate` for Pydantic errors
- [X] T007 [P] [US1] Write an async integration test for Spanish exceptions in `tests/integration/test_i18n.py`

**Checkpoint**: At this point, User Story 1 should be fully functional. The API translates errors into Spanish.

---

## Phase 4: User Story 2 - Receive error messages in English (Priority: P1)

**Goal**: As an API client using an English-configured interface, I want to receive all exception and validation errors in English.

**Independent Test**: Send an `Accept-Language: en` header and verify the JSON response is in English.

### Implementation for User Story 2

- [X] T008 [P] [US2] Create the English translation file in `app/locales/en.json`
- [X] T009 [US2] Modify `I18nService` in `app/core/i18n.py` to parse `Accept-Language` headers dynamically from the request context if needed, or ensure the global exception handler passes the locale correctly.
- [X] T010 [P] [US2] Write an async integration test for English exceptions in `tests/integration/test_i18n.py`

**Checkpoint**: English and Spanish translations both work independently based on the requested locale.

---

## Phase 5: User Story 3 - Fallback to Default Language (Priority: P2)

**Goal**: As a generic API client that does not specify a language, I want the API to gracefully fall back to a default language (Spanish).

**Independent Test**: Omit the header or request `fr`, and verify the API returns Spanish. Remove a key from `en.json` and verify it falls back to the Spanish string.

### Implementation for User Story 3

- [X] T011 [US3] Update `get_locale` in `app/api/deps.py` to explicitly fallback to `"es"` if the header is missing or unsupported.
- [X] T012 [US3] Update `I18nService.translate` in `app/core/i18n.py` to fallback to the default locale string if the specific key is missing in the requested language.
- [X] T013 [P] [US3] Write fallback integration tests in `tests/integration/test_i18n.py`

**Checkpoint**: All fallback edge cases are handled gracefully.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T014 [P] Document the new localization feature in `README.md`
- [X] T015 Run validation scenarios from `specs/001-api-localization/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories.
- **User Stories (Phase 3+)**: Must be executed in priority order (US1 → US2 → US3) since US2 builds on the global handlers introduced in US1, and US3 modifies the lookup logic built in US2.
- **Polish (Phase 6)**: Depends on all user stories being complete.

### Parallel Opportunities

- Creation of JSON locale files (T004, T008) can be done in parallel with testing tasks (T007, T010, T013).
- Setup (T001) can be done independently.
- Documentation (T014) can be done in parallel once the feature is stable.

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Setup and Foundational tasks.
2. Implement US1 (Spanish).
3. Validate using the quickstart scenarios.
4. Deploy the MVP (since Spanish is the native project language, this delivers immediate value without breaking anything).

### Incremental Delivery

1. Once the MVP is verified, add English support (US2).
2. Finally, harden the implementation by handling missing keys and fallbacks (US3).
