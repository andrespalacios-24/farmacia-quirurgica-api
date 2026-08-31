from fastapi import APIRouter, status
from sqlalchemy import select
from app.api.deps import DbSession
from app.core.domain_exceptions import DomainException

from app.schemas import PatientCreate, PatientResponse
from app.models import Patient

router = APIRouter(
    prefix="/patients",
    tags=["Patients"]
)

@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def register_patient(patient_in: PatientCreate, db: DbSession):
    new_patient = Patient(**patient_in.model_dump())
    db.add(new_patient)
    await db.commit()
    await db.refresh(new_patient)
    return new_patient

@router.get("/", response_model=list[PatientResponse], status_code=status.HTTP_200_OK)
async def get_patients(db: DbSession):
    query = select(Patient)
    result = await db.execute(query)
    patients_found = result.scalars().all()
    return patients_found

@router.get("/{national_id}", response_model=PatientResponse, status_code=status.HTTP_200_OK)
async def get_patient_by_national_id(national_id: str, db: DbSession):
    query = select(Patient).where(Patient.national_id == national_id)
    result = await db.execute(query)
    patient_found = result.scalar_one_or_none()
    
    if not patient_found:
        raise DomainException("errors.patient_not_found", status_code=404, national_id=national_id)
    
    return patient_found