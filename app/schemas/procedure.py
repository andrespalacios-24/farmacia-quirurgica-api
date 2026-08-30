from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from enum import Enum

class OperatingRoom(str, Enum):
    OR_1 = "Operating Room 1"
    OR_2 = "Operating Room 2"
    OR_3 = "Operating Room 3"  

class ProcedureBase(BaseModel):
    description: str = Field(..., max_length=255, examples=["Appendectomy", "Laparoscopic Cholecystectomy"])
    operating_room: OperatingRoom

class ProcedureCreate(ProcedureBase):
    patient_id: int = Field(..., description="Internal ID of the admitted patient")

class PatientSummary(BaseModel):
    id: int
    full_name: str     
    national_id: str   

    model_config = ConfigDict(from_attributes=True)

class ProcedureResponse(ProcedureBase):
    id: int
    patient: PatientSummary  
    procedure_date: datetime
    
    model_config = ConfigDict(from_attributes=True)