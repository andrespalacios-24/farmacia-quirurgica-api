from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api.deps import get_db

from app.schemas import PatientCreate, PatientResponse
from app.models import Patient

router = APIRouter(
    prefix="/patients",
    tags=["Patients"]
)

@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def register_patient(patient_in: PatientCreate, db: AsyncSession = Depends(get_db)):
    new_patient = Patient(**patient_in.model_dump())
    db.add(new_patient)
    await db.commit()
    await db.refresh(new_patient)
    return new_patient

@router.get("/", response_model=list[PatientResponse], status_code=status.HTTP_200_OK)
async def get_patients(db: AsyncSession = Depends(get_db)):
    query = select(Patient)
    result = await db.execute(query)
    patients_found = result.scalars().all()
    return patients_found

@router.get("/{national_id}", response_model=PatientResponse, status_code=status.HTTP_200_OK)
async def get_patient_by_national_id(national_id: str, db: AsyncSession = Depends(get_db)):
    query = select(Patient).where(Patient.national_id == national_id)
    result = await db.execute(query)
    patient_found = result.scalar_one_or_none()
    
    if not patient_found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Clinical history not found for ID {national_id}"
        )
    
    return patient_found