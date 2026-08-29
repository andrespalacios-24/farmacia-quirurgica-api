## 1. Database Model Mappings

- [x] 1.1 Rename attributes in `app/models/orm/` files to English and map them to the legacy Spanish column names (e.g. `patient_id = mapped_column("id_paciente")`). Verify by checking that models can be imported without syntax errors.

## 2. Pydantic Schemas

- [x] 2.1 Translate field names and model names in `app/schemas/` to English. Verify by checking that Pydantic schema files parse without syntax errors.

## 3. Core Configurations

- [x] 3.1 Translate internal variables, function names, and comments in `app/core/`, `app/database.py`, and `app/config.py` to English. Verify by ensuring the application boots up successfully with no import errors.

## 4. API Endpoints

- [x] 4.1 Update endpoint paths and internal function names in `app/routers/` to English. Ensure they import the newly translated Pydantic schemas and SQLAlchemy models. Verify by starting the FastAPI server and checking the auto-generated `/docs` interface for English routes.

## 5. Main Application

- [x] 5.1 Translate variables, descriptions, and comments in `app/main.py`. Verify by running the application and checking the root `GET /` endpoint response for English text.
- [x] 5.2 Translate `app/api/deps.py` and `app/seed.py` to English. Verify by successfully running `seed.py` (if applicable) or confirming no syntax errors.

## 6. Testing & Validation

- [x] 6.1 Start the FastAPI server and manually test the endpoints (e.g., `/supplies`, `/patients`) using tools like Swagger UI or curl to confirm they return the correct English payloads and successfully read from the Spanish database schema.
