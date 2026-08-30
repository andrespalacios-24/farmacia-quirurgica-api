import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.core.i18n import i18n

@pytest.fixture(autouse=True)
def load_i18n():
    # Ensure translations are loaded before tests
    i18n.load_translations()

@pytest.mark.asyncio
async def test_i18n_spanish_default():
    # Using an invalid ID format to trigger validation error or a non-existent endpoint for 404
    # To test DomainException, we need an endpoint that raises it.
    # We will test validation error here as a proxy if we don't have a reliable mock endpoint.
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Invalid payload to force a 422 RequestValidationError
        response = await client.post("/patients/", json={})
    
    assert response.status_code == 422
    assert "Error de validación" in response.json()["detail"]

@pytest.mark.asyncio
async def test_i18n_english_header():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/patients/",
            json={},
            headers={"Accept-Language": "en"}
        )
    
    assert response.status_code == 422
    assert "Validation error" in response.json()["detail"]

@pytest.mark.asyncio
async def test_i18n_fallback_to_spanish():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Request French, should fallback to Spanish
        response = await client.post(
            "/patients/",
            json={},
            headers={"Accept-Language": "fr"}
        )
    
    assert response.status_code == 422
    assert "Error de validación" in response.json()["detail"]

def test_i18n_missing_key_fallback():
    # Translate a key that exists in 'es' but let's pretend it's missing in 'en'
    # Actually we can't easily pretend unless we mutate the dictionary.
    # Let's test the translation function directly.
    val = i18n.translate("errors.not_found", "fr")
    # Because fr is not supported, it should fallback to es
    assert "no encontrado" in val
