# app/models/common.py
from typing import Annotated
from pydantic import BeforeValidator

# Pydantic v2 Validator para convertir ObjectId de Mongo a str automáticamente
PyObjectId = Annotated[str, BeforeValidator(lambda x: str(x) if x is not None else None)]