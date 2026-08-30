from typing import Any

class DomainException(Exception):
    """
    Excepción base para toda la lógica de negocio (El 'Paciente' principal de los errores).
    """
    def __init__(self, key: str, status_code: int = 400, **kwargs: Any):
        self.key = key
        self.kwargs = kwargs
        self.status_code = status_code
        super().__init__(self.key)

class NotFoundError(DomainException):
    """
    Equivalente a buscar instrumental que no está en la mesa de mayo.
    """
    def __init__(self, entity_name: str, entity_id: str | int):
        super().__init__("errors.not_found", status_code=404, entity_name=entity_name, entity_id=entity_id)

class BusinessLogicError(DomainException):
    """
    Equivalente a una incompatibilidad clínica (ej. estéril vs contaminado).
    Violación de reglas de negocio.
    """
    def __init__(self, detail: str):
        super().__init__("errors.business_logic", status_code=409, detail=detail)
