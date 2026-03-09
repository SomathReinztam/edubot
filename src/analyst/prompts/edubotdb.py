
DB_SKILL_1 = """
# Edubot

## 1. Visión general

Esta base de datos PostgreSQL respalda un sistema de **monitoreo y análisis automatizado de canales de Discord** para el ecosistema corporativo de **Solenium / Unergy**, empresas colombianas del sector de energía solar (minigranjas solares, comercialización de energía, logística de suministro). El sistema:

- Ingesta mensajes de múltiples servidores (guilds) de Discord.
- Genera resúmenes diarios por canal con decisiones, tareas, bloqueos y progreso.
- Detecta alertas automáticas (retrasos, anomalías, hitos).
- Compara actividad entre canales vinculados de distintos servidores (cross-guild reports).
- Expone datos vía API protegida por API keys.

**Motor:** PostgreSQL con extensiones de tipos ENUM personalizados.  
**Migraciones:** Alembic (versión actual: `a3b7c9d1e2f4`).  
**Zona horaria:** Todos los timestamps son `TIMESTAMP WITH TIME ZONE` (UTC).

---

## 2. Tipos ENUM personalizados

| Tipo               | Valores conocidos (inferidos de los datos)                        |
|--------------------|-------------------------------------------------------------------|
| `channellinktype`  | `MANUAL`, `NAME_MATCH` (posiblemente más)                        |
| `alertseverity`    | `INFO`, `WARNING`, `CRITICAL` (posiblemente más)                 |
| `alertstatus`      | `OPEN` (posiblemente `ACKNOWLEDGED`, `RESOLVED`)                 |
| `accesslevel`      | Desconocido (tabla vacía)                                         |
| `syncstatus`       | `SUCCESS`, `FAILED` (posiblemente más)                           |
| `companytype`      | `OTHER` (posiblemente más)                                       |

---

## 3. Esquema de tablas

### 3.1 `discord_guilds` — Servidores de Discord

Tabla raíz. Cada fila es un servidor (guild) de Discord monitoreado.

| Columna                  | Tipo            | Descripción                                      |
|--------------------------|-----------------|--------------------------------------------------|
| `id`                     | `BIGSERIAL` PK  | ID del guild (coincide con el ID real de Discord)|
| `name`                   | `VARCHAR(255)`  | Nombre del servidor                              |
| `icon_url`               | `TEXT`          | URL del ícono                                    |
| `is_active`              | `BOOLEAN`       | Si se monitorea activamente                      |
| `company_type`           | `companytype`   | Tipo de empresa                                  |
| `channels_discovered_at` | `TIMESTAMPTZ`   | Última vez que se descubrieron canales           |
| `created_at`             | `TIMESTAMPTZ`   | Fecha de registro                                |
| `updated_at`             | `TIMESTAMPTZ`   | Última actualización                             |

**Guilds conocidos (5):**

| ID                   | Nombre                   | Rol en el ecosistema                              |
|----------------------|--------------------------|---------------------------------------------------|
| `682685655234379909`  | Oficina virtual          | Servidor general / social de la empresa           |
| `772855809406271508`  | Unergy                   | Comercialización y operaciones de energía         |
| `913090735753011200`  | ZenTrack                 | Logística y seguimiento de suministro             |
| `974711817924386827`  | Solenium                 | Operaciones solares, proyectos de minigranjas     |
| `1308885706621452369` | The Sun Factory - Unergy | Compras de equipos (trackers, shelters, paneles)  |

---

### 3.2 `discord_channels` — Canales de Discord

| Columna               | Tipo            | Descripción                                              |
|------------------------|-----------------|----------------------------------------------------------|
| `id`                   | `BIGSERIAL` PK  | ID del canal (ID real de Discord)                        |
| `guild_id`             | `BIGINT` FK → `discord_guilds.id` | Servidor al que pertenece            |
| `name`                 | `VARCHAR(255)`  | Nombre del canal (sin `#`)                               |
| `channel_type`         | `VARCHAR(50)`   | Tipo: `text`, etc.                                       |
| `parent_channel_id`    | `BIGINT`        | Canal padre (categoría), nullable                        |
| `category_name`        | `VARCHAR(255)`  | Nombre de la categoría en Discord                        |
| `minifarm_project_id`  | `BIGINT`        | ID del proyecto de minigranja asociado (nullable)        |
| `minifarm_id`          | `BIGINT`        | ID de la minigranja asociada (nullable)                  |
| `project_code`         | `VARCHAR(255)`  | Código del proyecto (ej: código Solenium, nullable)      |
| `minifarm_name`        | `VARCHAR(255)`  | Nombre legible de la minigranja (nullable)               |
| `is_restricted`        | `BOOLEAN`       | Si requiere permisos especiales                          |
| `is_active`            | `BOOLEAN`       | Si está activo                                           |
| `has_schedule_posts`   | `BOOLEAN`       | Si tiene publicaciones de cronograma                     |
| `has_progress_posts`   | `BOOLEAN`       | Si tiene publicaciones de avance                         |
| `last_message_at`      | `TIMESTAMPTZ`   | Último mensaje detectado                                 |
| `created_at`           | `TIMESTAMPTZ`   | Registro en el sistema                                   |
| `updated_at`           | `TIMESTAMPTZ`   | Última actualización                                     |

**Categorías observadas:** `Clubes y comités`, `Solenium + Unergy`, `Originación`, `Inactivos`.

---

### 3.3 `discord_messages` — Mensajes crudos

Almacena mensajes individuales de Discord. **La tabla se vacía tras procesarse** (las 5 primeras filas están vacías en la muestra).

| Columna              | Tipo            | Descripción                                  |
|----------------------|-----------------|----------------------------------------------|
| `id`                 | `BIGSERIAL` PK  | ID del mensaje (ID real de Discord)          |
| `channel_id`         | `BIGINT` FK → `discord_channels.id` | Canal origen           |
| `author_id`          | `VARCHAR(50)`   | ID del autor en Discord                      |
| `author_name`        | `VARCHAR(255)`  | Nombre visible del autor                     |
| `content`            | `TEXT`          | Contenido del mensaje                        |
| `message_type`       | `VARCHAR(50)`   | Tipo de mensaje                              |
| `has_attachments`    | `BOOLEAN`       | Si tiene archivos adjuntos                   |
| `has_embeds`         | `BOOLEAN`       | Si tiene embeds                              |
| `attachment_urls`    | `JSON`          | Lista de URLs de adjuntos                    |
| `reply_to_id`        | `BIGINT`        | ID del mensaje al que responde (nullable)    |
| `thread_id`          | `BIGINT`        | ID del hilo (nullable)                       |
| `discord_created_at` | `TIMESTAMPTZ`   | Fecha original del mensaje en Discord        |
| `fetched_at`         | `TIMESTAMPTZ`   | Cuándo se descargó                           |
| `is_processed`       | `BOOLEAN`       | Si ya fue procesado para resúmenes/alertas   |

> **Nota:** Esta tabla probablemente se purga después de cada ciclo de sincronización. No esperes datos históricos aquí; los resúmenes están en `daily_summaries`.

---

### 3.4 `daily_summaries` — Resúmenes diarios por canal

Tabla central de análisis. Contiene un resumen generado por IA para cada canal por cada día.

| Columna            | Tipo            | Descripción                                          |
|--------------------|-----------------|------------------------------------------------------|
| `id`               | `BIGSERIAL` PK  | ID autoincremental                                   |
| `channel_id`       | `BIGINT` FK → `discord_channels.id` | Canal resumido               |
| `summary_date`     | `DATE`          | Fecha del resumen                                    |
| `summary_text`     | `TEXT`          | Resumen en prosa del día                             |
| `key_decisions`    | `JSON`          | Array de decisiones clave (puede estar vacío `[]`)   |
| `action_items`     | `JSON`          | Array de tareas: `{task, assigned_to, priority}`     |
| `blockers`         | `JSON`          | Array de bloqueos (strings)                          |
| `schedule_updates` | `JSON`          | Array de cambios de cronograma                       |
| `progress_updates` | `JSON`          | Array: `{item, details}`                             |
| `message_count`    | `INTEGER`       | Cantidad de mensajes del día                         |
| `unique_authors`   | `INTEGER`       | Autores únicos del día                               |
| `created_at`       | `TIMESTAMPTZ`   | Cuándo se generó el resumen                          |

**Constraint único:** `(channel_id, summary_date)` — un resumen por canal por día.

**Estructura de `action_items`:**
```json
[
  {
    "task": "Descripción de la tarea",
    "assigned_to": "Nombre de la persona o equipo",
    "priority": "high | medium | low"
  }
]
```

**Estructura de `progress_updates`:**
```json
[
  {
    "item": "Nombre del elemento",
    "details": "Descripción del avance"
  }
]
```

---

### 3.5 `discord_alerts` — Alertas detectadas

| Columna             | Tipo            | Descripción                                      |
|---------------------|-----------------|--------------------------------------------------|
| `id`                | `BIGSERIAL` PK  | ID autoincremental                               |
| `channel_id`        | `BIGINT` FK → `discord_channels.id` | Canal donde se detectó       |
| `guild_id`          | `BIGINT` FK → `discord_guilds.id`   | Servidor                     |
| `source_message_id` | `BIGINT`        | ID del mensaje fuente (nullable)                 |
| `severity`          | `alertseverity` | `INFO`, `WARNING`, `CRITICAL`                    |
| `status`            | `alertstatus`   | `OPEN`, posiblemente `ACKNOWLEDGED`, `RESOLVED`  |
| `category`          | `VARCHAR(100)`  | Categoría de la alerta (ver abajo)               |
| `title`             | `VARCHAR(500)`  | Título descriptivo                               |
| `description`       | `TEXT`          | Detalle completo                                 |
| `project_code`      | `VARCHAR(255)`  | Código del proyecto afectado (nullable)           |
| `minifarm_name`     | `VARCHAR(255)`  | Minigranja afectada (nullable)                   |
| `detected_at`       | `TIMESTAMPTZ`   | Cuándo se detectó                                |
| `acknowledged_at`   | `TIMESTAMPTZ`   | Cuándo se reconoció (nullable)                   |
| `resolved_at`       | `TIMESTAMPTZ`   | Cuándo se resolvió (nullable)                    |
| `acknowledged_by`   | `VARCHAR(255)`  | Quién la reconoció (nullable)                    |

**Categorías conocidas:** `schedule_delay`, `system_malfunction`, `milestone`, `budget`.

---

### 3.6 `channel_contexts` — Contexto acumulativo por canal

Resumen de largo plazo de cada canal generado por IA a partir del historial.

| Columna              | Tipo            | Descripción                                            |
|----------------------|-----------------|--------------------------------------------------------|
| `id`                 | `BIGSERIAL` PK  | ID autoincremental                                     |
| `channel_id`         | `BIGINT` FK → `discord_channels.id` UNIQUE | Canal (1:1)         |
| `context_summary`    | `TEXT`          | Resumen extenso en Markdown del propósito y estado     |
| `key_topics`         | `JSON`          | Array de temas clave (puede estar vacío)               |
| `key_people`         | `JSON`          | Array: `{name, message_count}`                         |
| `project_status`     | `TEXT`          | Estado del proyecto: `unknown`, etc.                   |
| `messages_analyzed`  | `INTEGER`       | Total de mensajes analizados para generar el contexto  |
| `oldest_message_date`| `TIMESTAMPTZ`   | Mensaje más antiguo analizado                          |
| `newest_message_date`| `TIMESTAMPTZ`   | Mensaje más reciente analizado                         |
| `created_at`         | `TIMESTAMPTZ`   | Creación del contexto                                  |
| `updated_at`         | `TIMESTAMPTZ`   | Última actualización                                   |

**Estructura de `key_people`:**
```json
[
  {"name": "Eduardo Ospina", "message_count": 33},
  {"name": "Sara Restrepo", "message_count": 33}
]
```

---

### 3.7 `channel_links` — Vínculos entre canales

Conecta canales de diferentes servidores que cubren el mismo tema.

| Columna        | Tipo            | Descripción                                          |
|----------------|-----------------|------------------------------------------------------|
| `id`           | `BIGSERIAL` PK  | ID autoincremental                                   |
| `channel_a_id` | `BIGINT` FK → `discord_channels.id` | Primer canal              |
| `channel_b_id` | `BIGINT` FK → `discord_channels.id` | Segundo canal             |
| `link_type`    | `channellinktype`| `MANUAL` o `NAME_MATCH`                             |
| `link_reason`  | `VARCHAR(500)`  | Razón legible del vínculo                            |
| `confidence`   | `INTEGER`       | 0-100, nivel de confianza                            |
| `is_active`    | `BOOLEAN`       | Si el vínculo está activo                            |
| `created_at`   | `TIMESTAMPTZ`   | Creación                                             |
| `updated_at`   | `TIMESTAMPTZ`   | Última actualización                                 |

**Constraint único:** `(channel_a_id, channel_b_id)` — un vínculo por par de canales.

---

### 3.8 `cross_guild_reports` — Reportes cruzados entre servidores

Compara la actividad diaria de dos canales vinculados para detectar discrepancias.

| Columna           | Tipo            | Descripción                                          |
|-------------------|-----------------|------------------------------------------------------|
| `id`              | `BIGSERIAL` PK  | ID autoincremental                                   |
| `report_date`     | `DATE`          | Fecha del reporte                                    |
| `channel_link_id` | `BIGINT` FK → `channel_links.id` | Vínculo analizado            |
| `channel_a_id`    | `BIGINT` FK → `discord_channels.id` | Canal A                   |
| `channel_b_id`    | `BIGINT` FK → `discord_channels.id` | Canal B                   |
| `guild_a_id`      | `BIGINT` FK → `discord_guilds.id`   | Servidor A                |
| `guild_b_id`      | `BIGINT` FK → `discord_guilds.id`   | Servidor B                |
| `comparison_text` | `TEXT`          | Resumen de la comparación                            |
| `discrepancies`   | `JSON`          | Array de discrepancias encontradas                   |
| `alignments`      | `JSON`          | Array: `{description, details}`                      |
| `recommendations` | `JSON`          | Array: `{description, priority}`                     |
| `has_discrepancies`| `BOOLEAN`      | Flag rápido de si hay discrepancias                  |
| `max_severity`    | `VARCHAR(50)`   | Severidad máxima: `info`, `critical`, etc.           |
| `created_at`      | `TIMESTAMPTZ`   | Cuándo se generó                                     |

**Constraint único:** `(channel_link_id, report_date)` — un reporte por vínculo por día.

**Estructura de `recommendations`:**
```json
[
  {
    "description": "Texto de la recomendación",
    "priority": "high | medium | low"
  }
]
```

---

### 3.9 `api_keys` — Llaves de API

| Columna      | Tipo            | Descripción                             |
|--------------|-----------------|----------------------------------------|
| `id`         | `BIGSERIAL` PK  | ID autoincremental                      |
| `app_name`   | `VARCHAR(255)` UNIQUE | Nombre de la aplicación            |
| `key_hash`   | `VARCHAR(128)` UNIQUE | Hash de la API key                 |
| `key_prefix` | `VARCHAR(8)`    | Prefijo visible (ej: `edk_29c2`)       |
| `created_by` | `VARCHAR(255)`  | Quién creó la key                       |
| `is_active`  | `BOOLEAN`       | Si está activa (default `true`)         |
| `last_used_at`| `TIMESTAMPTZ`  | Último uso (nullable)                   |
| `created_at` | `TIMESTAMPTZ`   | Creación                                |
| `revoked_at` | `TIMESTAMPTZ`   | Revocación (nullable)                   |

---

### 3.10 `discord_access_permissions` — Permisos de acceso

Tabla vacía en la muestra. Controla quién puede consultar qué canales/proyectos.

| Columna           | Tipo            | Descripción                                    |
|-------------------|-----------------|------------------------------------------------|
| `id`              | `BIGSERIAL` PK  | ID autoincremental                             |
| `user_identifier` | `VARCHAR(255)`  | Identificador del usuario                      |
| `user_name`       | `VARCHAR(255)`  | Nombre del usuario                             |
| `channel_id`      | `BIGINT`        | Canal permitido (nullable = todos)             |
| `project_code`    | `VARCHAR(255)`  | Proyecto permitido (nullable = todos)          |
| `access_level`    | `accesslevel`   | Nivel de acceso                                |
| `is_active`       | `BOOLEAN`       | Si el permiso está activo                      |
| `granted_by`      | `VARCHAR(255)`  | Quién otorgó el permiso                        |
| `granted_at`      | `TIMESTAMPTZ`   | Cuándo se otorgó                               |
| `expires_at`      | `TIMESTAMPTZ`   | Expiración (nullable = sin expiración)         |

**Constraint único:** `(user_identifier, channel_id, project_code)`.

---

### 3.11 `discord_query_log` — Log de consultas

Registra cada consulta hecha al sistema vía API.

| Columna               | Tipo            | Descripción                          |
|------------------------|-----------------|--------------------------------------|
| `id`                   | `BIGSERIAL` PK  | ID autoincremental                   |
| `user_identifier`      | `VARCHAR(255)`  | Quién consultó                       |
| `channel_id`           | `BIGINT`        | Canal consultado                     |
| `project_code`         | `VARCHAR(255)`  | Proyecto consultado                  |
| `question`             | `TEXT`          | Pregunta del usuario                 |
| `response_summary`     | `TEXT`          | Resumen de la respuesta              |
| `messages_fetched_live`| `INTEGER`       | Mensajes descargados en tiempo real  |
| `tokens_used`          | `INTEGER`       | Tokens de IA consumidos              |
| `duration_ms`          | `INTEGER`       | Duración en milisegundos             |
| `created_at`           | `TIMESTAMPTZ`   | Timestamp de la consulta             |
| `app_name`             | `VARCHAR(255)`  | Aplicación que hizo la consulta      |

---

### 3.12 `discord_sync_log` — Log de sincronización

| Columna               | Tipo            | Descripción                                      |
|------------------------|-----------------|--------------------------------------------------|
| `id`                   | `BIGSERIAL` PK  | ID autoincremental                               |
| `sync_type`            | `VARCHAR(50)`   | Tipo: `bootstrap`, `midnight`                    |
| `status`               | `syncstatus`    | `SUCCESS`, `FAILED`                              |
| `started_at`           | `TIMESTAMPTZ`   | Inicio                                           |
| `completed_at`         | `TIMESTAMPTZ`   | Fin                                              |
| `channels_processed`   | `INTEGER`       | Canales procesados                               |
| `messages_fetched`     | `INTEGER`       | Mensajes descargados                             |
| `summaries_generated`  | `INTEGER`       | Resúmenes creados                                |
| `alerts_created`       | `INTEGER`       | Alertas creadas                                  |
| `guild_ids_processed`  | `JSON`          | Array de IDs de guilds procesados                |
| `error_message`        | `TEXT`          | Mensaje de error (nullable)                      |
| `details`              | `JSON`          | Detalles adicionales (ej: `{skipped: reason}`)   |

---

### 3.13 `alembic_version` — Control de migraciones

| Columna       | Tipo           | Descripción                    |
|---------------|----------------|--------------------------------|
| `version_num` | `VARCHAR(32)` PK | Versión actual de migraciones |

Versión actual: `a3b7c9d1e2f4`.

---

## 4. Diagrama de relaciones (ER simplificado)

```
discord_guilds (1) ──< (N) discord_channels
                              │
              ┌───────────────┼───────────────────────┐
              │               │                       │
              ▼               ▼                       ▼
      discord_messages   daily_summaries       discord_alerts
                              │
                              │
      channel_contexts ──── (1:1) discord_channels
                              │
              ┌───────────────┴───────────────┐
              │                               │
       channel_links (channel_a, channel_b)
              │
              ▼
    cross_guild_reports

    api_keys                    (independiente)
    discord_access_permissions  (independiente, referencia lógica a channels)
    discord_query_log           (independiente, referencia lógica a channels)
    discord_sync_log            (independiente)
```

---

## 5. Patrones de consulta comunes

### Obtener resumen diario de un canal con nombre y servidor
```sql
SELECT ds.summary_date, dg.name AS guild, dc.name AS channel,
       ds.summary_text, ds.action_items, ds.blockers,
       ds.message_count, ds.unique_authors
FROM daily_summaries ds
JOIN discord_channels dc ON ds.channel_id = dc.id
JOIN discord_guilds dg ON dc.guild_id = dg.id
WHERE ds.summary_date = '2026-02-15'
ORDER BY ds.message_count DESC;
```

### Alertas abiertas por severidad
```sql
SELECT da.severity, da.category, da.title, da.description,
       dc.name AS channel, dg.name AS guild
FROM discord_alerts da
JOIN discord_channels dc ON da.channel_id = dc.id
JOIN discord_guilds dg ON da.guild_id = dg.id
WHERE da.status = 'OPEN'
ORDER BY
  CASE da.severity
    WHEN 'CRITICAL' THEN 1
    WHEN 'WARNING' THEN 2
    WHEN 'INFO' THEN 3
  END;
```

### Reportes cruzados con discrepancias
```sql
SELECT cgr.report_date, cgr.comparison_text, cgr.max_severity,
       cgr.discrepancies, cgr.recommendations,
       ca.name AS channel_a, cb.name AS channel_b,
       ga.name AS guild_a, gb.name AS guild_b
FROM cross_guild_reports cgr
JOIN discord_channels ca ON cgr.channel_a_id = ca.id
JOIN discord_channels cb ON cgr.channel_b_id = cb.id
JOIN discord_guilds ga ON cgr.guild_a_id = ga.id
JOIN discord_guilds gb ON cgr.guild_b_id = gb.id
WHERE cgr.has_discrepancies = true
ORDER BY cgr.report_date DESC;
```

### Personas más activas por canal (desde contextos)
```sql
SELECT dc.name AS channel, dg.name AS guild,
       cc.key_people, cc.messages_analyzed
FROM channel_contexts cc
JOIN discord_channels dc ON cc.channel_id = dc.id
JOIN discord_guilds dg ON dc.guild_id = dg.id
ORDER BY cc.messages_analyzed DESC;
```

### Estado del sistema de sincronización
```sql
SELECT sync_type, status, started_at, completed_at,
       channels_processed, messages_fetched,
       summaries_generated, alerts_created, error_message
FROM discord_sync_log
ORDER BY started_at DESC
LIMIT 10;
```

---

## 6. Notas para el agente

### Campos JSON
Los campos JSON (`key_decisions`, `action_items`, `blockers`, `discrepancies`, `alignments`, `recommendations`, `key_topics`, `key_people`, `attachment_urls`, `guild_ids_processed`, `details`) se almacenan como `JSON` (no `JSONB`). Para consultas con filtros sobre su contenido, usa operadores `::jsonb` para cast y luego operadores JSONB (`->`, `->>`, `@>`, `jsonb_array_elements`).

### IDs de Discord como PKs
Las tablas `discord_guilds`, `discord_channels` y `discord_messages` usan el **ID real de Discord** como primary key (no autoincremental de Postgres), aunque el tipo es `BIGSERIAL`. Esto significa que los IDs son números grandes de ~18 dígitos (snowflakes de Discord).

### Tabla `discord_messages` puede estar vacía
Los mensajes se procesan y probablemente se eliminan tras la generación de resúmenes. Para consultar historial, usa `daily_summaries` y `channel_contexts`.

### Idioma del contenido
Todo el contenido generado (resúmenes, alertas, contextos, reportes cruzados) está en **español**.

### Ciclos de sincronización
- `bootstrap`: Carga inicial de canales y mensajes históricos.
- `midnight`: Sincronización diaria automática a las 05:00 UTC.
- Si `details` contiene `{"skipped": "already_processed"}`, no había nuevos datos que procesar.

### Prioridades de tareas y recomendaciones
Se usan consistentemente: `high`, `medium`, `low`.

### Contexto de negocio
- **Solenium**: Operaciones de minigranjas solares, proyectos de construcción.
- **Unergy**: Comercialización de energía, plataforma de facturación.
- **ZenTrack**: Logística y cadena de suministro.
- **The Sun Factory - Unergy**: Compras de equipos solares.
- **Oficina virtual**: Servidor social/general.
- **uWatts**: Unidad de energía tokenizada usada internamente.
- **Commodities monitoreados**: Cobre, aluminio, zinc, plata (relevantes para manufactura solar).
"""
