from fastapi import APIRouter, status
from sqlalchemy import select
from app.api.deps import DbSession
from app.core.domain_exceptions import DomainException
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
    db: DbSession
):
    result = await db.execute(select(Patient).where(Patient.id == procedure_in.patient_id))
    patient_db = result.scalar_one_or_none()
    
    if not patient_db:
        raise DomainException("errors.patient_not_in_system", status_code=404)

    new_procedure = Procedure(**procedure_in.model_dump())
    
    db.add(new_procedure)
    await db.commit()
    
    post_op_query = select(Procedure).where(Procedure.id == new_procedure.id).options(selectinload(Procedure.patient))
    final_result = await db.execute(post_op_query)
    complete_procedure = final_result.scalar_one()
    
    return complete_procedure

@router.get("/", response_model=list[ProcedureResponse], status_code=status.HTTP_200_OK)
async def get_procedures(db: DbSession):
    query = select(Procedure).options(selectinload(Procedure.patient))
    result = await db.execute(query)
    procedures = result.scalars().all()
    return procedures
