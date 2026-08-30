## Purpose

Defines the new English-based API endpoints and JSON request/response structures for the system, replacing the legacy Spanish contracts.

## ADDED Requirements

### Requirement: English API Routes
The system SHALL expose REST API endpoints with English names for all resources, completely replacing the former Spanish paths.

#### Scenario: Accessing supplies
- **WHEN** a client makes a request to `/supplies` or `/supplies/{id}`
- **THEN** the system routes the request to the corresponding internal logic and returns a response.

#### Scenario: Accessing patients
- **WHEN** a client makes a request to `/patients` or `/patients/{id}`
- **THEN** the system routes the request to the corresponding internal logic and returns a response.

### Requirement: English JSON Payloads
The system SHALL accept and return JSON payloads where all field names and keys are written in English.

#### Scenario: Creating a supply
- **WHEN** a client sends a POST request with an English JSON body (e.g. `{"name": "...", "quantity": ...}`)
- **THEN** the system successfully validates the English fields and processes the request.

#### Scenario: Retrieving a patient
- **WHEN** a client retrieves a patient
- **THEN** the response JSON contains English keys (e.g. `{"id": "...", "first_name": "..."}`).
