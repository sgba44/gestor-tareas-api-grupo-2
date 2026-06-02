# Definición de los endpoints REST para la gestión de tareas

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from aplicacion.base_de_datos import get_db
from aplicacion.esquemas import TaskCreate, TaskResponse, TaskUpdate
from aplicacion.modelos import Task, TaskPriority, TaskStatus

# Router con prefijo /tasks; agrupa todos los endpoints de tareas
router = APIRouter(prefix="/tasks", tags=["tasks"])


def get_task_or_404(task_id: int, db: Session) -> Task:
    """Busca una tarea por id y la devuelve, o lanza 404 si no existe.

    Args:
        task_id (int): Identificador único de la tarea a buscar.
        db (Session): Sesión activa de SQLAlchemy proporcionada por
            inyección de dependencias.

    Returns:
        Task: Instancia del modelo ORM correspondiente a la tarea
            encontrada.

    Raises:
        HTTPException: Si no existe una tarea con el ``task_id``
            proporcionado (código 404).
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return task


# Devuelve la lista completa de tareas almacenadas
@router.get("/", response_model=List[TaskResponse])
def list_tasks(db: Session = Depends(get_db)):
    """Devuelve la lista completa de tareas almacenadas.

    Args:
        db (Session): Sesión activa de SQLAlchemy inyectada
            automáticamente por FastAPI.

    Returns:
        list[Task]: Lista con todas las instancias de ``Task``
            presentes en la base de datos.
    """
    return db.query(Task).all()


# Devuelve una tarea por su identificador; 404 si no existe
@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """Obtiene una tarea individual por su identificador.

    Args:
        task_id (int): Identificador único de la tarea solicitada.
        db (Session): Sesión activa de SQLAlchemy inyectada
            automáticamente por FastAPI.

    Returns:
        Task: Instancia del modelo ORM correspondiente a la tarea.

    Raises:
        HTTPException: Si no existe una tarea con el ``task_id``
            proporcionado (código 404).
    """
    return get_task_or_404(task_id, db)


# Crea una nueva tarea y devuelve el recurso creado con código 201
@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    """Crea una nueva tarea y la persiste en la base de datos.

    Args:
        payload (TaskCreate): Esquema Pydantic con los datos de la
            nueva tarea (``title`` obligatorio, ``description``,
            ``status`` y ``priority`` opcionales).
        db (Session): Sesión activa de SQLAlchemy inyectada
            automáticamente por FastAPI.

    Returns:
        Task: Instancia del modelo ORM de la tarea recién creada,
            incluyendo el ``id`` y ``created_at`` generados por la
            base de datos.
    """
    task = Task(**payload.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


# Actualiza parcialmente una tarea; solo modifica los campos enviados en el cuerpo
@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db)):
    """Actualiza parcialmente una tarea existente.

    Solo modifica los campos incluidos en el cuerpo de la petición.
    No permite actualizar tareas cuyo estado sea ``done``.

    Args:
        task_id (int): Identificador único de la tarea a actualizar.
        payload (TaskUpdate): Esquema Pydantic con los campos a
            modificar (``title``, ``description``, ``status`` y
            ``priority``, todos opcionales).
        db (Session): Sesión activa de SQLAlchemy inyectada
            automáticamente por FastAPI.

    Returns:
        Task: Instancia del modelo ORM de la tarea con los campos
            actualizados.

    Raises:
        HTTPException: Si no existe una tarea con el ``task_id``
            proporcionado (código 404) o si la tarea tiene estado
            ``done`` (código 400).
    """
    task = get_task_or_404(task_id, db)
    if task.status == TaskStatus.done:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update a completed task",
        )
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


# Elimina una tarea de la base de datos; devuelve 204 sin cuerpo
@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Elimina una tarea de la base de datos.

    Args:
        task_id (int): Identificador único de la tarea a eliminar.
        db (Session): Sesión activa de SQLAlchemy inyectada
            automáticamente por FastAPI.

    Returns:
        None: Respuesta vacía con código de estado 204.

    Raises:
        HTTPException: Si no existe una tarea con el ``task_id``
            proporcionado (código 404).
    """
    task = get_task_or_404(task_id, db)
    db.delete(task)
    db.commit()


# Elimina todas las tareas de la base de datos; devuelve 204 sin cuerpo
@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_all_tasks(db: Session = Depends(get_db)):
    """Elimina todas las tareas de la base de datos.

    Args:
        db (Session): Sesión activa de SQLAlchemy inyectada
            automáticamente por FastAPI.

    Returns:
        None: Respuesta vacía con código de estado 204.
    """
    db.query(Task).delete()
    db.commit()
