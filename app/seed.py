import asyncio
from pwdlib import PasswordHash

# Importamos el creador de sesiones asíncronas de tu configuración de BD
from app.database import AsyncSessionLocal # (Ajusta el nombre según como lo tengas en database.py)

# Importamos los modelos ORM de tu módulo RBAC
from app.models.orm.rbac import Permiso, Rol, Usuario

# Inicializamos pwdlib usando su configuración recomendada (típicamente bcrypt)
password_hash = PasswordHash.recommended()

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# ==========================================
# 1. FUENTE DE VERDAD (DATA STRUCTURES)
# ==========================================

# Lista plana de todos los permisos atómicos del sistema
PERMISOS_BASE = [
    "usuarios:crear",
    "usuarios:leer",
    "insumos:crear",
    "insumos:retirar",
    "insumos:devolver",
    "reportes:leer"
]

# Diccionario que mapea cada ROL con los permisos exactos que le corresponden
ROLES_BASE = {
    "ADMIN": PERMISOS_BASE,  # El Admin hereda todos los permisos listados arriba
    "INSTRUMENTADOR": [
        "insumos:retirar", 
        "insumos:devolver"
    ],
    "FARMACEUTICO": [
        "insumos:crear", 
        "insumos:retirar", 
        "insumos:devolver", 
        "reportes:leer"
    ],
    "CIRUJANO": [
        "reportes:leer"
    ],
    "ANESTESIOLOGO": [
        "insumos:retirar", 
        "insumos:devolver",
        "reportes:leer"
    ]
}

# Datos del superusuario fundador
ADMIN_USER = {
    "email": "admin@farmacia.quirurgica",
    "nombre_completo": "Administrador Principal",
    # NOTA: En un entorno real, esta clave debería venir de tu archivo .env
    "password_plana": "Cirugia2026*" 
}

# ==========================================
# 2. FUNCIONES DE INSERCIÓN (IDEMPOTENTES)
# ==========================================

async def seed_permisos(session: AsyncSession):
    print("--- Sembrando Permisos Base ---")
    
    for codigo_permiso in PERMISOS_BASE:
        # 1. Construimos la consulta usando 'Permiso.codigo'
        stmt = select(Permiso).where(Permiso.codigo == codigo_permiso)
        resultado = await session.execute(stmt)
        permiso_existente = resultado.scalar_one_or_none()
        
        # 2. Si no existe en la BD, lo instanciamos asignando el valor a 'codigo'
        if not permiso_existente:
            nuevo_permiso = Permiso(codigo=codigo_permiso)
            session.add(nuevo_permiso)
            print(f"[+] Permiso creado: {codigo_permiso}")
        else:
            print(f"[=] Permiso ya existe: {codigo_permiso}")
            
    # 3. Confirmamos la transacción
    await session.commit()

#--------------------------------------------------------------------
# ROLES
#--------------------------------------------------------------------

async def seed_roles(session: AsyncSession):
    print("--- Sembrando Roles y Relaciones ---")
    
    # Iteramos sobre el diccionario (clave: nombre_rol, valor: codigos_permisos)
    for nombre_rol, codigos_permisos in ROLES_BASE.items():
        
        # 1. Verificamos si el rol ya existe
        stmt_rol = select(Rol).where(Rol.nombre == nombre_rol)
        resultado_rol = await session.execute(stmt_rol)
        rol_existente = resultado_rol.scalar_one_or_none()
        
        if not rol_existente:
            # 2. Instanciamos el rol
            nuevo_rol = Rol(nombre=nombre_rol)
            
            # 3. Buscamos TODOS los permisos que le corresponden de una sola vez
            stmt_permisos = select(Permiso).where(Permiso.codigo.in_(codigos_permisos))
            resultado_permisos = await session.execute(stmt_permisos)
            permisos_db = resultado_permisos.scalars().all()
            
            # 4. Asignamos los objetos de la BD a la relación M:N del rol
            nuevo_rol.permisos = list(permisos_db)
            
            # 5. Agregamos a la sesión
            session.add(nuevo_rol)
            print(f"[+] Rol creado y vinculado: {nombre_rol}")
        else:
            print(f"[=] Rol ya existe: {nombre_rol}")
            
    # 6. Guardamos los cambios
    await session.commit()

async def seed_admin(session: AsyncSession):
    print("--- Sembrando Usuario Administrador ---")
    
    # 1. Buscamos si el admin ya existe por su email
    stmt = select(Usuario).where(Usuario.email == ADMIN_USER["email"])
    resultado = await session.execute(stmt)
    admin_existente = resultado.scalar_one_or_none()
    
    if not admin_existente:
        # 2. Hasheamos la contraseña de forma segura
        hashed_password = password_hash.hash(ADMIN_USER["password_plana"])
        
        # 3. Creamos el usuario
        nuevo_admin = Usuario(
            email=ADMIN_USER["email"],
            nombre_completo=ADMIN_USER["nombre_completo"],
            password=hashed_password,  # Guardamos el hash, NUNCA la contraseña plana
            activo=True
        )
        
        # 4. Buscamos el rol ADMIN en la BD para asignárselo
        stmt_rol = select(Rol).where(Rol.nombre == "ADMIN")
        rol_admin = (await session.execute(stmt_rol)).scalar_one()
        
        # 5. Vinculamos el rol y guardamos
        nuevo_admin.roles = [rol_admin]
        
        session.add(nuevo_admin)
        print(f"[+] Usuario Admin creado: {ADMIN_USER['email']}")
    else:
        print(f"[=] Usuario Admin ya existe: {ADMIN_USER['email']}")
        
    await session.commit()

# ==========================================
# 3. BLOQUE DE EJECUCIÓN PRINCIPAL
# ==========================================

async def run_seed():
    print("Iniciando proceso de Seeding...")
    async with AsyncSessionLocal() as session:
        # El orden es ESTRICTO: primero permisos, luego roles, luego usuarios
        await seed_permisos(session)
        await seed_roles(session)
        await seed_admin(session)
    print("Proceso de Seeding finalizado con éxito.")

if __name__ == "__main__":
    asyncio.run(run_seed())