# API Farmacia Quirúrgica 🏥💊
> **API RESTful asíncrona para la gestión, entrega en farmacia y trazabilidad en tiempo real de insumos médicos en quirófano.**

---

## 📌 Descripción del Proyecto
Sistema diseñado para digitalizar y optimizar el control de trazabilidad de insumos médicos durante intervenciones quirúrgicas. Permite a los roles del quirófano (instrumentadores, auxiliares, anestesiólogos) realizar solicitudes incrementales de insumos, paquetes preconfigurados (kits) y gestionar el despacho en farmacia hospitalaria con control de inventario en tiempo real.

---

## 🛠️ Tecnologías Utilizadas
* **Lenguaje:** Python 3.12+
* **Framework Web:** FastAPI
* **Base de Datos:** PostgreSQL 16 (Relacional)
* **ORM:** SQLAlchemy 2.0 (100% asíncrono con AsyncSession) y Alembic
* **Validación de Datos:** Pydantic v2 & Pydantic Settings
* **Servidor ASGI:** Uvicorn
* **Entorno de Desarrollo:** Ubuntu (WSL2) en Windows 11

---

## Main Features 🚀

- **Robust Backend**: Asynchronous endpoints using FastAPI and `asyncpg` with PostgreSQL.
- **Relational Design**: SQLAlchemy ORM for complex relationships (Users, Roles, Permissions).
- **Secure Authentication**: JWT-based stateless authentication with Role-Based Access Control (RBAC).
- **Internationalization (i18n)**: Global localization support returning error messages and exceptions dynamically based on the client's `Accept-Language` header (Supports English and Spanish).
- **Clean Architecture**: Strong separation of concerns through Services, Routers, Models, and centralized exception handling.

---

## 📂 Estructura del Proyecto
```text
farmacia-quirurgica-api/
├── app/
│   ├── main.py          # Punto de entrada FastAPI y Swagger UI
│   ├── config.py        # Lectura y validación de variables de entorno
│   ├── database.py      # Cliente asíncrono para PostgreSQL
│   ├── models/          # Modelos de datos en SQLAlchemy
│   ├── schemas/         # Validaciones DTO en Pydantic v2
│   ├── services/        # Capa de lógica de negocio (NUEVO)
│   └── routers/         # Controladores de rutas HTTP
├── .env.example         # Plantilla de variables de entorno
├── .gitignore           # Exclusión de archivos sensibles
└── requirements.txt     # Dependencias del proyecto