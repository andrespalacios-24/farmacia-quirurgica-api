import asyncio
from pwdlib import PasswordHash

# Import the async session creator from the DB configuration
from app.database import AsyncSessionLocal 

# Import the ORM models
from app.models import Permission, Role, User, Supply, Batch, Patient

# Initialize pwdlib using its recommended configuration (typically bcrypt)
password_hash = PasswordHash.recommended()

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# ==========================================
# 1. SOURCE OF TRUTH (DATA STRUCTURES)
# ==========================================

# Flat list of all atomic permissions in the system
BASE_PERMISSIONS = [
    "users:create",
    "users:read",
    "supplies:create",
    "supplies:withdraw",
    "supplies:return",
    "reports:read"
]

# Dictionary mapping each ROLE to the exact permissions they correspond to
BASE_ROLES = {
    "ADMIN": BASE_PERMISSIONS,  # Admin inherits all permissions listed above
    "INSTRUMENTALIST": [
        "supplies:withdraw", 
        "supplies:return"
    ],
    "PHARMACIST": [
        "supplies:create", 
        "supplies:withdraw", 
        "supplies:return", 
        "reports:read"
    ],
    "SURGEON": [
        "reports:read"
    ],
    "ANESTHESIOLOGIST": [
        "supplies:withdraw", 
        "supplies:return",
        "reports:read"
    ],
    "CIRCULATING": [
    "supplies:withdraw",
    "supplies:return"
    ]   
}

# Data of the founding superuser
ADMIN_USER = {
    "username": "main_admin", 
    "email": "admin@surgical.pharmacy",
    "full_name": "Main Administrator",
    "plain_password": "Surgery2026*"
}

BASE_PATIENTS = [
    {
        "national_id": "100200300", 
        "full_name": "Patient Trauma One"
    },
    {
        "national_id": "400500600", 
        "full_name": "Patient Appendectomy Two"
    }
]

BASE_SUPPLIES = [
    {
        "barcode": "SUT-VIC-01",
        "name": "Suture Vicryl 1 CT-1",
        "minimum_stock": 10
    },
]

BASE_BATCHES = [
    {
        "barcode": "SUT-VIC-01",
        "batch_number": "L-2026-08A",
        "expiration_date": None,
        "current_stock": 50
    },
]


# ==========================================
# 2. INSERTION FUNCTIONS (IDEMPOTENT)
# ==========================================

async def seed_permissions(session: AsyncSession):
    print("--- Seeding Base Permissions ---")
    
    for permission_code in BASE_PERMISSIONS:
        stmt = select(Permission).where(Permission.code == permission_code)
        result = await session.execute(stmt)
        existing_permission = result.scalar_one_or_none()
        
        if not existing_permission:
            new_permission = Permission(code=permission_code)
            session.add(new_permission)
            print(f"[+] Permission created: {permission_code}")
        else:
            print(f"[=] Permission already exists: {permission_code}")
            
    await session.commit()

#--------------------------------------------------------------------
# ROLES
#--------------------------------------------------------------------

async def seed_roles(session: AsyncSession):
    print("--- Seeding Roles and Relationships ---")
    
    for role_name, permission_codes in BASE_ROLES.items():
        
        stmt_role = select(Role).where(Role.name == role_name)
        result_role = await session.execute(stmt_role)
        existing_role = result_role.scalar_one_or_none()
        
        if not existing_role:
            new_role = Role(name=role_name)
            
            stmt_permissions = select(Permission).where(Permission.code.in_(permission_codes))
            result_permissions = await session.execute(stmt_permissions)
            db_permissions = result_permissions.scalars().all()
            
            new_role.permissions = list(db_permissions)
            
            session.add(new_role)
            print(f"[+] Role created and linked: {role_name}")
        else:
            print(f"[=] Role already exists: {role_name}")
            
    await session.commit()

async def seed_admin(session: AsyncSession):
    print("--- Seeding Administrator User ---")
    
    stmt = select(User).where(User.email == ADMIN_USER["email"])
    result = await session.execute(stmt)
    existing_admin = result.scalar_one_or_none()
    
    if not existing_admin:
        hashed_password = password_hash.hash(ADMIN_USER["plain_password"])
        
        new_admin = User(
            username=ADMIN_USER["username"],
            email=ADMIN_USER["email"],
            full_name=ADMIN_USER["full_name"],
            hashed_password=hashed_password, 
            is_active=True
        )
        
        stmt_role = select(Role).where(Role.name == "ADMIN")
        admin_role = (await session.execute(stmt_role)).scalar_one()
        
        new_admin.roles = [admin_role]
        
        session.add(new_admin)
        print(f"[+] Admin User created: {ADMIN_USER['email']}")
    else:
        print(f"[=] Admin User already exists: {ADMIN_USER['email']}")
        
    await session.commit()

async def seed_supplies(session: AsyncSession):
    print("--- Entering Supplies to Pharmacy ---")
    
    for supply_data in BASE_SUPPLIES:
        
        stmt = select(Supply).where(Supply.barcode == supply_data["barcode"])
        result = await session.execute(stmt)
        existing_supply = result.scalar_one_or_none()
        
        if not existing_supply:
            new_supply = Supply(**supply_data)
            
            session.add(new_supply)
            print(f"[+] Supply entered: {supply_data['name']}")
        else:
            print(f"[=] Supply already on shelf: {supply_data['name']}")
            
    await session.commit()

async def seed_batches(session: AsyncSession):
    print("--- Entering Batches to Pharmacy ---")

    for batch_data in BASE_BATCHES:
        stmt_supply = select(Supply).where(Supply.barcode == batch_data["barcode"])
        result_supply = await session.execute(stmt_supply)
        db_supply = result_supply.scalar_one_or_none()

        if not db_supply:
            print(f"[!] Supply not found for batch {batch_data['batch_number']}")
            continue

        stmt_batch = select(Batch).where(
            (Batch.supply_id == db_supply.id) & (Batch.batch_number == batch_data["batch_number"])
        )
        result_batch = await session.execute(stmt_batch)
        existing_batch = result_batch.scalar_one_or_none()

        if not existing_batch:
            new_batch = Batch(
                supply_id=db_supply.id,
                batch_number=batch_data["batch_number"],
                expiration_date=batch_data.get("expiration_date"),
                current_stock=batch_data["current_stock"],
            )
            session.add(new_batch)
            print(f"[+] Batch entered: {batch_data['batch_number']}")
        else:
            print(f"[=] Batch already exists: {batch_data['batch_number']}")

    await session.commit()

async def seed_patients(session: AsyncSession):
    print("--- Opening Admissions: Entering Base Patients ---")
    
    for patient_data in BASE_PATIENTS:
        
        stmt = select(Patient).where(Patient.national_id == patient_data["national_id"])
        result = await session.execute(stmt)
        existing_patient = result.scalar_one_or_none()
        
        if not existing_patient:
            new_patient = Patient(**patient_data)
            
            session.add(new_patient)
            print(f"[+] Patient admitted: {patient_data['full_name']}")
        else:
            print(f"[=] Patient already has an open clinical history: {patient_data['full_name']}")
            
    await session.commit()

# ==========================================
# 3. MAIN EXECUTION BLOCK
# ==========================================

async def run_seed():
    print("Starting Seeding process...")
    async with AsyncSessionLocal() as session:
        # STRICT ORDER: first permissions, then roles, then users
        await seed_permissions(session)
        await seed_roles(session)
        await seed_admin(session)
        await seed_patients(session)
        await seed_supplies(session)
        await seed_batches(session)
    print("Seeding process successfully finished.")
    

if __name__ == "__main__":
    asyncio.run(run_seed())
