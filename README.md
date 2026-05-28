# API de Gestión de Tareas

API REST para gestionar el ciclo de vida de tareas, construida con **FastAPI** y **SQLAlchemy**. Permite crear, consultar, actualizar parcialmente y eliminar tareas. Cada tarea cuenta con un identificador único, título, descripción opcional, estado (`pending`, `in_progress`, `done`) y fecha de creación asignada automáticamente.

## Requisitos previos

| Requisito | Versión mínima |
|-----------|---------------|
| Python    | 3.12+         |
| pip       | 23+           |

### Dependencias del proyecto

| Paquete    | Versión  | Propósito                                |
|------------|----------|------------------------------------------|
| FastAPI    | 0.136.1  | Framework web asíncrono                  |
| SQLAlchemy | 2.0.49   | ORM para el acceso a base de datos       |
| Pydantic   | 2.13.4   | Validación y serialización de datos      |
| Uvicorn    | 0.46.0   | Servidor ASGI de desarrollo/producción   |
| pytest     | 9.0.3    | Framework de tests (desarrollo)          |
| httpx      | 0.28.1   | Cliente HTTP para tests (desarrollo)     |
| anyio      | 4.13.0   | Soporte asíncrono para tests (desarrollo)|

## Instalación

1. **Clonar el repositorio:**

   ```bash
   git clone https://github.com/sgba44/gestor-tareas-api-grupo-2.git
   cd gestor-tareas-api-grupo-2
   ```

2. **Crear y activar un entorno virtual:**

   ```bash
   python -m venv venv

   # macOS / Linux
   source venv/bin/activate

   # Windows
   venv\Scripts\activate
   ```

3. **Instalar las dependencias:**

   ```bash
   pip install -r requirements.txt
   ```

## Arrancar la aplicación

```bash
uvicorn aplicacion.principal:app --reload
```

La API quedará disponible en `http://127.0.0.1:8000`.

La documentación interactiva (Swagger UI) se genera automáticamente en `http://127.0.0.1:8000/docs`.

## Endpoints

La API expone cinco endpoints bajo el prefijo `/tasks`.

### 1. Listar todas las tareas

| Campo  | Valor                    |
|--------|--------------------------|
| Método | `GET`                    |
| Ruta   | `/tasks/`                |
| Params | Ninguno                  |

**Ejemplo de petición:**

```bash
curl http://127.0.0.1:8000/tasks/
```

**Ejemplo de respuesta** (`200 OK`):

```json
[
  {
    "id": 1,
    "title": "Revisar pull request",
    "description": "Revisar PR #42 del módulo de autenticación",
    "status": "pending",
    "created_at": "2026-05-28T10:00:00"
  }
]
```

---

### 2. Obtener una tarea por id

| Campo  | Valor                              |
|--------|------------------------------------|
| Método | `GET`                              |
| Ruta   | `/tasks/{task_id}`                 |
| Params | `task_id` (int) — Id de la tarea   |

**Ejemplo de petición:**

```bash
curl http://127.0.0.1:8000/tasks/1
```

**Ejemplo de respuesta** (`200 OK`):

```json
{
  "id": 1,
  "title": "Revisar pull request",
  "description": "Revisar PR #42 del módulo de autenticación",
  "status": "pending",
  "created_at": "2026-05-28T10:00:00"
}
```

**Ejemplo de error** (`404 Not Found`):

```json
{
  "detail": "Task not found"
}
```

---

### 3. Crear una nueva tarea

| Campo  | Valor                                                                 |
|--------|-----------------------------------------------------------------------|
| Método | `POST`                                                                |
| Ruta   | `/tasks/`                                                             |
| Body   | JSON con `title` (str, obligatorio), `description` (str, opcional), `status` (str, opcional; por defecto `"pending"`) |

Valores válidos para `status`: `"pending"`, `"in_progress"`, `"done"`.

**Ejemplo de petición:**

```bash
curl -X POST http://127.0.0.1:8000/tasks/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Escribir tests", "description": "Cubrir los endpoints de tareas"}'
```

**Ejemplo de respuesta** (`201 Created`):

```json
{
  "id": 2,
  "title": "Escribir tests",
  "description": "Cubrir los endpoints de tareas",
  "status": "pending",
  "created_at": "2026-05-28T10:05:00"
}
```

**Ejemplo de error** (`422 Unprocessable Entity`):

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "title"],
      "msg": "Field required",
      "input": {}
    }
  ]
}
```

---

### 4. Actualizar parcialmente una tarea

| Campo  | Valor                                                                 |
|--------|-----------------------------------------------------------------------|
| Método | `PATCH`                                                               |
| Ruta   | `/tasks/{task_id}`                                                    |
| Params | `task_id` (int) — Id de la tarea                                      |
| Body   | JSON con los campos a modificar: `title` (str), `description` (str), `status` (str) — todos opcionales |

> **Regla de negocio:** no se permite actualizar una tarea cuyo estado sea `done`.

**Ejemplo de petición:**

```bash
curl -X PATCH http://127.0.0.1:8000/tasks/2 \
  -H "Content-Type: application/json" \
  -d '{"status": "in_progress"}'
```

**Ejemplo de respuesta** (`200 OK`):

```json
{
  "id": 2,
  "title": "Escribir tests",
  "description": "Cubrir los endpoints de tareas",
  "status": "in_progress",
  "created_at": "2026-05-28T10:05:00"
}
```

**Ejemplo de error — tarea no encontrada** (`404 Not Found`):

```json
{
  "detail": "Task not found"
}
```

**Ejemplo de error — tarea completada** (`400 Bad Request`):

```json
{
  "detail": "Cannot update a completed task"
}
```

---

### 5. Eliminar una tarea

| Campo  | Valor                              |
|--------|------------------------------------|
| Método | `DELETE`                           |
| Ruta   | `/tasks/{task_id}`                 |
| Params | `task_id` (int) — Id de la tarea   |

**Ejemplo de petición:**

```bash
curl -X DELETE http://127.0.0.1:8000/tasks/1
```

**Respuesta exitosa:** `204 No Content` (sin cuerpo).

**Ejemplo de error** (`404 Not Found`):

```json
{
  "detail": "Task not found"
}
```

## Ejecutar los tests

```bash
pytest tests/ -v
```

Los tests utilizan una base de datos SQLite separada para garantizar aislamiento y no afectar al archivo `tareas.db` de producción.

## Estructura del proyecto

```
gestor-tareas-api-grupo-2/
├── aplicacion/                 # Paquete principal de la aplicación
│   ├── __init__.py
│   ├── principal.py            # Punto de entrada: instancia FastAPI y registro de routers
│   ├── base_de_datos.py        # Configuración del engine y sesión de SQLAlchemy
│   ├── modelos.py              # Modelos ORM (tabla tasks, enum TaskStatus)
│   ├── esquemas.py             # Esquemas Pydantic de entrada y respuesta
│   └── rutas/                  # Definición de endpoints agrupados por recurso
│       ├── __init__.py
│       └── tareas.py           # Endpoints REST de tareas (CRUD)
├── tests/                      # Suite de tests automatizados
│   ├── __init__.py
│   └── test_tasks.py           # Tests de los endpoints de tareas
├── .devin/                     # Configuración del agente Devin
│   └── AGENTS.md               # Instrucciones y convenciones del proyecto
├── .gitignore
├── requirements.txt            # Dependencias del proyecto
└── README.md
```
