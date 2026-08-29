from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api.deps import get_db
from app.models import Procedure, Patient
from app.schemas import ProcedureCreate, ProcedureResponse
from sqlalchemy.orm import selectinload

router = APIRouter(
    prefix="/procedures",
    tags=["Procedures"]
)

@router.post("/", response_model=ProcedureResponse, status_code=status.HTTP_201_CREATED)
async def register_procedure(
    procedure_in: ProcedureCreate, 
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Patient).where(Patient.id == procedure_in.patient_id))
    patient_db = result.scalar_one_or_none()
    
    if not patient_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Error: The indicated patient is not found in the system."
        )

    new_procedure = Procedure(**procedure_in.model_dump())
    
    db.add(new_procedure)
    await db.commit()
    
    post_op_query = select(Procedure).where(Procedure.id == new_procedure.id).options(selectinload(Procedure.patient))
    final_result = await db.execute(post_op_query)
    complete_procedure = final_result.scalar_one()
    
    return complete_procedure

@router.get("/", response_model=list[ProcedureResponse], status_code=status.HTTP_200_OK)
async def get_procedures(db: AsyncSession = Depends(get_db)):
    query = select(Procedure).options(selectinload(Procedure.patient))
    result = await db.execute(query)
    procedures = result.scalars().all()
    return procedures
