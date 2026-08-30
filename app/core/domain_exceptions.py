from typing import Any

class DomainException(Exception):
    """
    Base exception for all business logic.
    """
    def __init__(self, key: str, status_code: int = 400, **kwargs: Any):
        self.key = key
        self.kwargs = kwargs
        self.status_code = status_code
        super().__init__(self.key)

class NotFoundError(DomainException):
    """
    Equivalent to searching for an instrument that is not on the instrument table.
    """
    def __init__(self, entity_name: str, entity_id: str | int):
        super().__init__("errors.not_found", status_code=404, entity_name=entity_name, entity_id=entity_id)

class BusinessLogicError(DomainException):
    """
    Equivalent to a clinical incompatibility (e.g., sterile vs contaminated).
    Violation of business rules.
    """
    def __init__(self, detail: str):
        super().__init__("errors.business_logic", status_code=409, detail=detail)
