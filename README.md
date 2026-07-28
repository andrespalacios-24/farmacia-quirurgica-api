# API Farmacia Quirúrgica 🏥💊
> **API RESTful asíncrona para la gestión, entrega en farmacia y trazabilidad en tiempo real de insumos médicos en quirófano.**

---

## 📌 Descripción del Proyecto
Sistema diseñado para digitalizar y optimizar el control de trazabilidad de insumos médicos durante intervenciones quirúrgicas. Permite a los roles del quirófano (instrumentadores, auxiliares, anestesiólogos) realizar solicitudes incrementales de insumos, paquetes preconfigurados (kits) y gestionar el despacho en farmacia hospitalaria con control de inventario en tiempo real.

---

## 🛠️ Tecnologías Utilizadas
* **Lenguaje:** Python 3.12+
* **Framework Web:** FastAPI
* **Base de Datos:** MongoDB Atlas (NoSQL)
* **Driver Asíncrono:** Motor
* **Validación de Datos:** Pydantic v2 & Pydantic Settings
* **Servidor ASGI:** Uvicorn
* **Entorno de Desarrollo:** Ubuntu (WSL2) en Windows 11

---

## 📂 Estructura del Proyecto
```text
farmacia-quirurgica-api/
├── app/
│   ├── main.py          # Punto de entrada FastAPI y Swagger UI
│   ├── config.py        # Lectura y validación de variables de entorno
│   ├── database.py      # Cliente asíncrono Motor para MongoDB
│   ├── models/          # Modelos de datos en Pydantic v2
│   └── routers/         # Controladores de rutas HTTP (En desarrollo)
├── .env.example         # Plantilla de variables de entorno
├── .gitignore           # Exclusión de archivos sensibles
└── requirements.txt     # Dependencias del proyecto