# Analisis de Cobertura de Tests

**Fecha:** 2026-06-23
**Cobertura global:** 91% (96 sentencias, 9 sin cubrir)
**Tests ejecutados:** 12 (todos pasaron)

## Reporte completo

| Modulo | Sentencias | Sin cubrir | Cobertura | Lineas sin cubrir |
|---|---|---|---|---|
| `aplicacion/__init__.py` | 0 | 0 | 100% | — |
| `aplicacion/base_de_datos.py` | 12 | 4 | **67%** | 24-28 |
| `aplicacion/esquemas.py` | 19 | 0 | 100% | — |
| `aplicacion/modelos.py` | 15 | 0 | 100% | — |
| `aplicacion/principal.py` | 6 | 0 | 100% | — |
| `aplicacion/rutas/__init__.py` | 0 | 0 | 100% | — |
| `aplicacion/rutas/tareas.py` | 44 | 5 | **89%** | 34, 74, 156-158 |

---

## Los 3 modulos con menor cobertura

### 1. `aplicacion/base_de_datos.py` — 67% (4 lineas sin cubrir)

**Lineas no cubiertas:** 24-28 (cuerpo completo de `get_db()`)

```python
def get_db():
    db = SessionLocal()       # linea 24
    try:                      # linea 25
        yield db              # linea 26
    finally:                  # linea 27
        db.close()            # linea 28
```

**Por que no esta cubierto:**
Los tests sustituyen `get_db` mediante `app.dependency_overrides`, por lo que la
implementacion real de produccion nunca se ejecuta. El generador completo —crear sesion,
cederla y cerrarla— queda sin ejercitar.

**Casos que faltan:**
- Verificar que `get_db()` produce (`yield`) una sesion valida de SQLAlchemy.
- Verificar que la sesion se cierra correctamente al terminar el generador (rama `finally`).
- Verificar el comportamiento si `SessionLocal()` lanza una excepcion.

**Esfuerzo estimado: Bajo**
Se puede resolver con 1-2 tests unitarios que invoquen `get_db()` como generador
(usando `next()`) y comprueben que devuelve un objeto `Session` y que `.close()` se llama.
No requiere cambios de arquitectura.

---

### 2. `aplicacion/rutas/tareas.py` — 89% (5 lineas sin cubrir)

**Lineas no cubiertas:** 34, 74, 156-158

**Detalle por linea:**

| Linea(s) | Funcion / Endpoint | Que falta |
|---|---|---|
| **34** | `get_task_or_404()` | La rama que lanza `HTTPException(404)` — ningun test consulta una tarea inexistente |
| **74** | `GET /tasks/{id}` (`get_task`) | El endpoint completo no tiene ningun test |
| **156-158** | `DELETE /tasks/{id}` (`delete_task`) | El endpoint completo no tiene ningun test |

**Casos que faltan:**

*Endpoint `GET /tasks/{id}` (linea 74):*
- Happy path: crear una tarea y obtenerla por id, esperando 200 con datos correctos.
- Error: solicitar un id inexistente, esperando 404 con `detail: "Tarea no encontrada"`.

*Endpoint `DELETE /tasks/{id}` (lineas 156-158):*
- Happy path: crear una tarea, eliminarla por id, esperando 204, confirmar que ya no existe.
- Error: eliminar un id inexistente, esperando 404 con `detail: "Tarea no encontrada"`.

*Funcion `get_task_or_404` (linea 34):*
- Se cubrira automaticamente al anadir los tests de error 404 de los endpoints anteriores.

*Endpoint `PATCH /tasks/{id}` con tarea inexistente:*
- Aunque el endpoint tiene tests, ninguno prueba el caso 404. Anadir un test que haga
  PATCH a un id inexistente, esperando 404.

**Esfuerzo estimado: Bajo**
Se necesitan ~5 tests nuevos, todos siguiendo el mismo patron que los existentes
(usar `client` fixture y `_create_task` helper). No requiere cambios de codigo ni
infraestructura de test adicional.

---

### 3. `aplicacion/principal.py` — 100% (0 lineas sin cubrir, pero sin tests dedicados)

**Nota:** Este modulo alcanza 100% de cobertura de lineas de forma indirecta, porque se
importa al crear el `TestClient(app)`. Sin embargo, **no tiene tests dedicados** que
verifiquen su comportamiento de inicializacion.

```python
Base.metadata.create_all(bind=engine)                    # linea 9
app = FastAPI(title="API de Gestion de Tareas")          # linea 12
app.include_router(tareas.router)                        # linea 15
```

**Casos que podrian anadirse (mejora de calidad, no de cobertura):**
- Verificar que `app.title` es `"API de Gestion de Tareas"`.
- Verificar que las rutas registradas incluyen el prefijo `/tasks`.
- Verificar que `GET /docs` devuelve 200 (Swagger UI disponible).
- Verificar que las tablas se crean correctamente al inicializar.

**Esfuerzo estimado: Bajo**
Son tests de "smoke" simples (2-3 tests). No aumentan la cobertura de lineas pero si
la confianza en la configuracion de la aplicacion.

---

## Resumen de esfuerzos

| Modulo | Cobertura actual | Cobertura estimada tras cubrir | Esfuerzo |
|---|---|---|---|
| `base_de_datos.py` | 67% | 100% | **Bajo** (~2 tests) |
| `rutas/tareas.py` | 89% | 100% | **Bajo** (~5 tests) |
| `principal.py` | 100% (indirecta) | 100% (directa) | **Bajo** (~3 tests) |

**Impacto global:** Anadiendo ~10 tests se puede llevar la cobertura del proyecto al
**100%** y eliminar todos los gaps funcionales detectados.
