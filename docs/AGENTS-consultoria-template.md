# Instrucciones para Devin — Template para Proyectos de Consultoría

<!--
  TEMPLATE GENÉRICO — Adaptar las secciones marcadas con [ADAPTAR] al proyecto concreto del cliente.
  Última revisión: 2026-06-23
-->

> **Propósito de este documento:** Definir las reglas y restricciones que Devin debe seguir al
> trabajar con código de cliente en proyectos de consultoría. El objetivo es garantizar seguridad,
> trazabilidad y cumplimiento normativo en cada interacción con el repositorio.

---

## 1. Descripción del proyecto

<!-- [ADAPTAR] Breve descripción funcional del proyecto del cliente. -->

| Capa              | Tecnología         |
|-------------------|--------------------|
| Framework web     | <!-- [ADAPTAR] --> |
| ORM / Acceso BD   | <!-- [ADAPTAR] --> |
| Base de datos     | <!-- [ADAPTAR] --> |
| Tests             | <!-- [ADAPTAR] --> |
| Lenguaje/Runtime  | <!-- [ADAPTAR] --> |

---

## 2. Archivos protegidos — No modificar sin aprobación explícita

Devin **NUNCA** debe modificar los siguientes archivos o directorios sin que el responsable del
proyecto lo autorice de forma explícita en la conversación:

### 2.1 Configuración de producción

- Archivos de configuración de entornos productivos o staging:
  - `*.prod.env`, `*.production.*`, `.env.production`
  - `config/production.*`, `settings/production.*`
  - Cualquier archivo cuyo nombre contenga `prod` o `production`
- Archivos de variables de entorno que no sean de desarrollo local:
  - `.env` (raíz), `.env.staging`, `.env.shared`
- Configuración de bases de datos de producción:
  - Scripts de migración ya aplicados en producción
  - Archivos de seed o fixtures de producción

### 2.2 CI/CD

- Pipelines y workflows:
  - `.github/workflows/*`
  - `.gitlab-ci.yml`, `Jenkinsfile`, `azure-pipelines.yml`
  - `.circleci/`, `buildspec.yml`, `.drone.yml`
- Configuración de despliegue:
  - `Dockerfile`, `docker-compose.yml`, `docker-compose.prod.yml`
  - `Procfile`, `app.yaml`, `fly.toml`, `render.yaml`
  - Manifiestos de Kubernetes (`k8s/`, `manifests/`, `helm/`)
- Políticas de seguridad del repositorio:
  - `.github/CODEOWNERS`, branch protection rules
  - `.npmrc` con configuración de seguridad

### 2.3 Infraestructura como código (IaC)

- Terraform: `*.tf`, `*.tfvars`, `.terraform.lock.hcl`
- CloudFormation: `template.yaml`, `*.cfn.yml`
- Pulumi: `Pulumi.yaml`, `Pulumi.*.yaml`
- Ansible: `playbooks/`, `inventory/`, `roles/`
- CDK: `cdk.json`, `lib/*Stack*`
- Cualquier directorio `infra/`, `infrastructure/`, `deploy/`, `iac/`

### 2.4 Procedimiento de aprobación

Si una tarea requiere modificar algún archivo protegido, Devin debe:

1. **Informar** al usuario listando los archivos exactos que necesita modificar y por qué.
2. **Esperar** confirmación explícita antes de realizar cualquier cambio.
3. **Documentar** la aprobación en la descripción del PR correspondiente.
4. Si la aprobación no llega, buscar una alternativa que no toque archivos protegidos.

---

## 3. Gestión de datos sensibles

### 3.1 Principio general

Devin trabaja bajo el supuesto de que **todo el código del cliente puede contener información
confidencial**. Debe tratar el código con la misma discreción que un consultor en las
instalaciones del cliente.

### 3.2 Datos sensibles en el código

Si Devin encuentra datos sensibles en el código fuente (PII, datos de negocio, datos de clientes
finales):

1. **No copiar** datos sensibles en mensajes, logs, comentarios de PR ni commits.
2. **No mover** datos sensibles a otros archivos o servicios externos.
3. **Notificar** al usuario de forma privada (vía `message_user`) indicando:
   - El archivo y línea donde se encontraron.
   - El tipo de dato sensible (PII, datos financieros, datos de salud, etc.).
   - Una recomendación de mitigación (externalizar a variables de entorno, cifrar, etc.).
4. **No incluir** datos sensibles en ejemplos de código, snippets, ni en la descripción del PR.

### 3.3 Credenciales expuestas

Si Devin detecta credenciales en el repositorio (API keys, tokens, contraseñas, certificados,
claves privadas), debe:

1. **Detener** inmediatamente cualquier tarea en curso relacionada con esos archivos.
2. **Alertar** al usuario con prioridad alta (`message_user` con `block_on_user=true`) indicando:
   - Archivo(s) y línea(s) exactos.
   - Tipo de credencial encontrada.
   - Riesgo asociado (acceso a qué sistema/servicio).
3. **Recomendar** acciones inmediatas:
   - Rotar la credencial comprometida.
   - Eliminar la credencial del historial de git (`git filter-branch` o BFG Repo Cleaner).
   - Mover la credencial a un gestor de secretos (Vault, AWS Secrets Manager, etc.).
   - Añadir el patrón al `.gitignore`.
4. **No hacer commit** de ningún archivo que contenga credenciales, ni siquiera para "moverlas".
5. **No ejecutar** código que utilice credenciales expuestas sin autorización explícita.

### 3.4 Archivos que nunca deben incluirse en commits

```gitignore
# Secretos y credenciales
.env
.env.*
!.env.example
*.pem
*.key
*.p12
*.pfx
credentials.json
service-account*.json
*secret*.*

# Bases de datos locales con datos reales
*.db
*.sqlite3
*.sql (dumps con datos reales)

# Archivos temporales con información sensible
*.log
.bash_history
.python_history
```

---

## 4. Política de ramas y commits

### 4.1 Ramas protegidas — Prohibición de commits directos

Devin **NUNCA** debe hacer push directo a las siguientes ramas:

- `main` / `master`
- `develop` / `development`
- `staging` / `release/*`
- `production` / `prod`
- Cualquier rama definida como protegida en la configuración del repositorio

Todo cambio a estas ramas debe llegar **exclusivamente** a través de Pull Requests revisados y
aprobados.

### 4.2 Naming de ramas

Formato obligatorio para ramas creadas por Devin:

```
devin/<timestamp>-<tipo>-<descripcion-corta>
```

Donde:
- `<timestamp>`: Epoch en segundos (`$(date +%s)`) para trazabilidad temporal.
- `<tipo>`: Uno de los siguientes prefijos:
  - `feat` — Nueva funcionalidad
  - `fix` — Corrección de bug
  - `refactor` — Refactorización sin cambio funcional
  - `docs` — Cambios en documentación
  - `test` — Añadir o modificar tests
  - `chore` — Tareas de mantenimiento
  - `security` — Correcciones de seguridad
- `<descripcion-corta>`: Slug en kebab-case, máximo 5 palabras.

**Ejemplos:**
```
devin/1719532800-feat-add-user-endpoint
devin/1719532800-fix-null-pointer-login
devin/1719532800-security-remove-exposed-key
```

### 4.3 Naming de commits

Formato obligatorio:

```
<tipo>: <descripción breve en imperativo>
```

- Un commit por cambio lógico. No mezclar cambios no relacionados.
- La descripción debe ser clara y en el idioma acordado con el cliente
  <!-- [ADAPTAR] definir idioma: castellano / inglés -->.
- Máximo 72 caracteres en la primera línea.
- Si es necesario, añadir cuerpo con contexto adicional separado por una línea en blanco.

**Tipos válidos:** `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `security`, `perf`

**Ejemplos:**
```
feat: añadir endpoint de búsqueda por categoría
fix: corregir validación de email en registro
security: eliminar API key expuesta de configuración
```

### 4.4 Prohibiciones de git

- **No usar** `--force` en ramas compartidas. Solo `--force-with-lease` en ramas propias de Devin.
- **No usar** `--no-verify` para saltar hooks de pre-commit.
- **No hacer** `git add .`; añadir archivos específicos.
- **No modificar** la configuración de git (`git config`).
- **No hacer** amend de commits ya pusheados.

---

## 5. Pull Requests — Contenido obligatorio

Cada PR creado por Devin debe incluir **todas** las secciones siguientes:

### 5.1 Template de PR

```markdown
## Resumen

<!-- Qué cambió y por qué, en 2-3 oraciones. -->

## Tipo de cambio

- [ ] Nueva funcionalidad (feat)
- [ ] Corrección de bug (fix)
- [ ] Refactorización (refactor)
- [ ] Documentación (docs)
- [ ] Tests (test)
- [ ] Seguridad (security)
- [ ] Otro: ___

## Archivos protegidos modificados

<!-- Si se modificó algún archivo de §2, indicar cuáles y adjuntar la aprobación explícita. -->
<!-- Si no se modificó ninguno, escribir: "Ninguno" -->

## Cambios realizados

<!-- Lista de cambios concretos con referencia a archivos y líneas relevantes. -->
<!-- Usar pseudo-diffs o fragmentos de código cuando ayude a la comprensión. -->

## Datos sensibles

<!-- Confirmar que NO se incluyen credenciales, PII ni datos de cliente en el diff. -->
<!-- Si se detectaron datos sensibles durante el desarrollo, describir las acciones tomadas. -->
- [ ] He verificado que no hay credenciales ni datos sensibles en los cambios.
- [ ] No se han copiado datos de producción en tests ni fixtures.

## Cómo probar

<!-- Pasos exactos para verificar los cambios. Incluir comandos, URLs y resultados esperados. -->

1. <!-- Paso 1 -->
2. <!-- Paso 2 -->
3. <!-- Resultado esperado -->

## Tests

- [ ] Se añadieron/actualizaron tests para los cambios.
- [ ] Todos los tests existentes siguen pasando.
- [ ] Los tests cubren happy path y casos de error.

## Documentación

- [ ] Docstrings actualizados en funciones modificadas.
- [ ] README actualizado si cambia la interfaz pública (endpoints, CLI, etc.).

## Checklist de seguridad

- [ ] Sin credenciales hardcodeadas.
- [ ] Sin datos sensibles en logs o mensajes de error.
- [ ] Inputs del usuario validados/sanitizados.
- [ ] Sin nuevas dependencias sin versión fijada.
- [ ] Dependencias nuevas publicadas hace más de 7 días.
```

### 5.2 Reglas adicionales de PR

- Cada PR debe ser **lo más pequeño posible**: un cambio lógico por PR.
- Si un cambio es grande, proponer dividirlo en PRs incrementales.
- Siempre ejecutar linting y tests antes de crear el PR.
- Incluir capturas de pantalla si hay cambios visuales.
- Nunca incluir archivos generados (builds, lockfiles no gestionados, etc.) salvo que sea
  intencionado.

---

## 6. Convenciones de código

<!-- [ADAPTAR] las siguientes secciones al stack y estilo del cliente. -->

### 6.1 Idioma

<!-- [ADAPTAR] Definir la política de idioma del proyecto. Ejemplo: -->
- **Código** (variables, funciones, clases): inglés.
- **Comentarios y documentación**: <!-- [ADAPTAR] castellano / inglés -->.
- **Mensajes de commit y PR**: <!-- [ADAPTAR] castellano / inglés -->.

### 6.2 Estilo de código

<!-- [ADAPTAR] Definir linter, formatter, reglas principales. Ejemplo: -->
- Seguir el linter/formatter configurado en el proyecto (<!-- [ADAPTAR] eslint/prettier/ruff/black/etc. -->).
- No desactivar reglas del linter sin justificación documentada.
- Importaciones ordenadas y agrupadas según convención del proyecto.

### 6.3 Tests

<!-- [ADAPTAR] Definir framework de tests y reglas. Ejemplo: -->
- Todo código nuevo debe tener tests que cubran happy path y al menos un caso de error.
- No conectar tests a bases de datos de producción.
- No hardcodear datos de cliente en tests; usar factories o fixtures genéricos.

---

## 7. Respuesta ante incidentes de seguridad

Si durante el trabajo Devin identifica cualquier problema de seguridad (credenciales expuestas,
vulnerabilidades, datos sensibles comprometidos):

| Prioridad | Situación | Acción de Devin |
|-----------|-----------|-----------------|
| **CRÍTICA** | Credenciales activas expuestas en el repositorio | Bloquear y alertar inmediatamente al usuario. No continuar hasta recibir instrucciones. |
| **ALTA** | Datos PII de clientes finales en el código | Alertar al usuario. No incluir esos datos en ningún output. |
| **MEDIA** | Vulnerabilidad conocida en dependencia | Informar al usuario con CVE y severidad. Proponer actualización si es compatible. |
| **BAJA** | Mala práctica de seguridad (ej: logging excesivo) | Informar al usuario. Corregir si está dentro del alcance de la tarea. |

---

## 8. Restricciones generales de consultoría

1. **Principio de mínimo privilegio**: Devin solo debe acceder y modificar lo estrictamente
   necesario para completar la tarea asignada.
2. **No exfiltración**: No enviar código del cliente a servicios externos, APIs de terceros ni
   repositorios fuera de la organización del cliente.
3. **No persistencia innecesaria**: No guardar datos del cliente en archivos temporales que no
   estén gestionados por el proyecto.
4. **Respeto al scope**: Si la tarea requiere acceso a sistemas fuera del repositorio (bases de
   datos, servicios cloud, paneles de administración), pedir autorización al usuario antes de
   proceder.
5. **Trazabilidad**: Cada acción de Devin debe ser rastreable a través de commits, PRs y mensajes.
   No realizar cambios "silenciosos" ni fuera del flujo de git.

---

## 9. Personalización por proyecto

<!-- Las siguientes secciones deben completarse al inicio de cada proyecto de cliente. -->

### 9.1 Contactos autorizados

| Rol | Nombre | Puede aprobar cambios protegidos |
|-----|--------|----------------------------------|
| Tech Lead | <!-- [ADAPTAR] --> | Sí |
| Desarrollador | <!-- [ADAPTAR] --> | <!-- Sí/No --> |

### 9.2 Entornos

| Entorno | Rama asociada | Devin puede hacer push |
|---------|---------------|------------------------|
| Producción | `main` | No |
| Staging | `staging` | No |
| Desarrollo | `develop` | Solo vía PR |

### 9.3 Herramientas de proyecto

| Herramienta | Uso |
|-------------|-----|
| Linter | <!-- [ADAPTAR] ej: ruff, eslint --> |
| Formatter | <!-- [ADAPTAR] ej: black, prettier --> |
| Tests | <!-- [ADAPTAR] ej: pytest, jest --> |
| CI/CD | <!-- [ADAPTAR] ej: GitHub Actions, GitLab CI --> |
| Gestor de secretos | <!-- [ADAPTAR] ej: Vault, AWS SM --> |
