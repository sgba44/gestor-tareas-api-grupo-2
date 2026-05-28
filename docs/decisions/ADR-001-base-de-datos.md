# ADR-001: Elección de SQLite como base de datos

## Estado

**Aceptado**

## Fecha

2026-05-28

## Contexto

La API de Gestión de Tareas necesita una base de datos relacional para persistir tareas con sus atributos (título, descripción, estado y fecha de creación). El proyecto se desarrolla con FastAPI y SQLAlchemy como ORM, lo que permite cambiar de motor de base de datos con un impacto mínimo en el código.

Requisitos clave del proyecto al momento de tomar esta decisión:

- **Entorno de desarrollo local**: la API se ejecuta en máquinas de los desarrolladores sin necesidad de infraestructura externa.
- **Modelo de datos sencillo**: una única tabla `tasks` con cinco columnas y sin relaciones complejas.
- **Equipo reducido**: el equipo de desarrollo es pequeño y busca minimizar la carga operativa.
- **Prototipado rápido**: se prioriza la velocidad de iteración y la facilidad de configuración inicial.
- **Sin requisitos de concurrencia elevada**: no se esperan múltiples escrituras simultáneas ni un volumen alto de peticiones concurrentes.

## Decisión

Se elige **SQLite** como motor de base de datos para la aplicación.

La base de datos se almacena como un archivo local (`tareas.db`) en el directorio raíz del proyecto. La conexión se configura mediante SQLAlchemy con el parámetro `check_same_thread=False` para permitir el uso de la conexión desde múltiples hilos en FastAPI.

```python
SQLALCHEMY_DATABASE_URL = "sqlite:///./tareas.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
```

### Razones principales

1. **Cero configuración**: SQLite no requiere instalar ni administrar un servidor de base de datos. El archivo se crea automáticamente al iniciar la aplicación.
2. **Incluido en Python**: el módulo `sqlite3` forma parte de la biblioteca estándar de Python, por lo que no se necesitan dependencias adicionales de sistema.
3. **Portabilidad**: la base de datos es un único archivo que se puede copiar, respaldar o eliminar fácilmente.
4. **Ideal para desarrollo y testing**: permite crear bases de datos en memoria (`:memory:`) para tests rápidos y aislados, como se hace actualmente con `StaticPool` en el test suite.
5. **Suficiente para el alcance actual**: el modelo de datos es simple y el volumen de operaciones esperado está dentro de las capacidades de SQLite.

## Alternativas consideradas

### PostgreSQL

| Aspecto | Detalle |
|---------|---------|
| **Ventajas** | Motor robusto para producción con soporte completo de ACID. Excelente manejo de concurrencia mediante MVCC. Tipos de datos avanzados (JSON, arrays, hstore). Amplio ecosistema de herramientas de monitorización y backup. Escalabilidad horizontal mediante réplicas de lectura. |
| **Inconvenientes** | Requiere instalar y configurar un servidor independiente. Añade complejidad operativa (gestión de usuarios, permisos, conexiones). Todos los desarrolladores necesitan tener PostgreSQL en su máquina o usar un contenedor Docker. Mayor consumo de recursos del sistema. Sobrecarga innecesaria para un modelo de datos con una sola tabla. |

### MySQL

| Aspecto | Detalle |
|---------|---------|
| **Ventajas** | Muy extendido en la industria con amplia comunidad. Buen rendimiento en operaciones de lectura intensiva. Herramientas maduras de administración (MySQL Workbench, phpMyAdmin). Soporte de replicación y clustering nativo. |
| **Inconvenientes** | También requiere un servidor dedicado con su configuración asociada. Soporte de transacciones dependiente del motor de almacenamiento (InnoDB vs MyISAM). Menor riqueza de tipos de datos comparado con PostgreSQL. Históricamente más permisivo con datos inválidos (modos estrictos opcionales). Licencia dual (GPL/comercial) que puede generar consideraciones legales en algunos contextos. |

## Consecuencias

### Positivas

- **Arranque inmediato**: cualquier desarrollador puede clonar el repositorio y ejecutar la API sin instalar software adicional.
- **Tests rápidos y aislados**: el uso de bases de datos en memoria elimina la necesidad de limpiar estado entre tests y acelera significativamente la suite de pruebas.
- **Simplicidad operativa**: no hay servidores que mantener, monitorizar ni actualizar.
- **Menor barrera de entrada**: nuevos miembros del equipo pueden contribuir desde el primer momento sin configurar infraestructura de base de datos.

### Negativas y riesgos a largo plazo

- **Concurrencia limitada**: SQLite utiliza un bloqueo a nivel de archivo para escrituras. Si la aplicación escala a múltiples instancias o recibe un volumen alto de escrituras concurrentes, se producirán cuellos de botella.
- **No apta para producción a gran escala**: si la API se despliega en un entorno de producción con alta disponibilidad, será necesario migrar a PostgreSQL u otro motor cliente-servidor.
- **Sin acceso remoto nativo**: la base de datos solo es accesible desde el proceso que la abre. No se pueden conectar herramientas externas de análisis o monitorización sin acceso al sistema de archivos.
- **Funcionalidades SQL limitadas**: SQLite no soporta `ALTER TABLE` completo, tipos de datos estrictos por defecto ni algunas funciones avanzadas de SQL estándar. Esto puede requerir migraciones más complejas si el esquema evoluciona.
- **Migración futura**: el uso de SQLAlchemy como capa de abstracción mitiga en gran medida el coste de una futura migración, ya que el cambio de motor se limita a la cadena de conexión y ajustes menores de configuración.

### Plan de mitigación

Si el proyecto crece más allá del alcance actual, se recomienda:

1. Migrar a **PostgreSQL** como primera opción para producción.
2. Aprovechar SQLAlchemy para que el cambio sea transparente al código de la aplicación.
3. Mantener SQLite como opción para desarrollo local y ejecución de tests.
