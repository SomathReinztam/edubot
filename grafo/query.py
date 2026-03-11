"""
Consultas en lenguaje natural al grafo Neo4j.

Uso:
    python3 -m grafo.query
"""

import os
import json
from neo4j import GraphDatabase
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()

# ── Conexión Neo4j ──────────────────────────────────────────────────────────
URI      = "bolt://localhost:7687"
USER     = "neo4j"
PASSWORD = "dulcinea2000."
driver   = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

# ── LLM ────────────────────────────────────────────────────────────────────
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.0,
    google_api_key=os.getenv("GOOGLE_API_KEY"),
)

# ── Esquema del grafo (para el contexto del LLM) ────────────────────────────
GRAPH_SCHEMA = """
Etiquetas de nodos: PERSONA, CONCEPTO, ORGANIZACION, LUGAR, PROYECTO,
DEPARTAMENTO, DOCUMENTO, TIEMPO, CODIGO, CONTRATO, EVENTO, SISTEMA,
PROCESO, OBJETO, GRUPO.

Propiedades comunes de nodos: name (string), description (string).

Tipos de relaciones más importantes (hay muchas más):
PERTENECE_A, VISITA, VISITO, VISITARA, LLEGA_A, LLEGO_A, IRA_A, VA_A,
HABLA_CON, HABLO_CON, SOLICITA, SOLICITAR, REQUIERE, NECESITA,
COORDINAR_CON, REUNION_CON, ENVIO, ENVIAR_A, PREGUNTA_POR, PREGUNTO_POR,
INFORMA_A, RECIBIO_SOLICITUD_DE, ESTA_EN, ESTA_LLEGANDO_A, UBICADO_EN,
RELACIONADO_CON, TIENE, TIENE_TRAMITES_EN, RADICAR, RADICAR_EN,
HACER_MANTENIMIENTO_EN, FIRMO, FIRME, PASO_PENDIENTES_A, INVENTARIO,
IR_A, IR_CON, MENCIONA, CONSIDERA, RECIBE_A.

El grafo representa conversaciones de un canal de Discord sobre
coordinación de visitas de campo, mantenimiento, trámites, personas
y lugares asociados a un proyecto de infraestructura.
"""

# ── Prompts ─────────────────────────────────────────────────────────────────
SYSTEM_CYPHER = """
Eres un experto en Neo4j y Cypher. Dado el esquema de un grafo y una
pregunta en lenguaje natural, genera UNA SOLA query Cypher válida que
responda la pregunta.

Reglas OBLIGATORIAS:
- Devuelve SOLO la query Cypher, sin explicaciones, sin bloques markdown.
- Usa LIMIT 50 si el resultado puede ser muy grande.
- Usa comparaciones case-insensitive con toLower() cuando busques por nombre.
- Si la pregunta no se puede responder con el grafo, devuelve: RETURN "SIN_DATOS"
- SIEMPRE nombra la relación en el MATCH: MATCH (a)-[r]->(b)
- Para obtener el tipo de relación usa type(r), NUNCA re-traverses el grafo en el RETURN.
- NO uses expresiones como type(last(relationships(...))), usa type(r) directamente.
- Ejemplo correcto:
    MATCH (a {{name: "X"}})-[r]->(b)
    RETURN a.name, type(r), b.name

Esquema del grafo:
{schema}
"""

SYSTEM_RESPUESTA = """
Eres un asistente que explica resultados de consultas a bases de datos
de grafos de forma clara y natural en español.

Se te dará:
1. La pregunta original del usuario.
2. La query Cypher ejecutada.
3. Los resultados crudos de la base de datos.

Tu tarea: responde la pregunta del usuario usando los resultados, en
lenguaje natural, sin jerga técnica. Si no hay resultados, dilo claramente.
Sé conciso pero completo.
"""


# ── Funciones ───────────────────────────────────────────────────────────────
def generar_cypher(pregunta: str) -> str:
    messages = [
        SystemMessage(content=SYSTEM_CYPHER.format(schema=GRAPH_SCHEMA)),
        HumanMessage(content=pregunta),
    ]
    respuesta = llm.invoke(messages)
    cypher = respuesta.content.strip()
    # limpiar bloques markdown si el modelo los incluye igual
    if cypher.startswith("```"):
        cypher = cypher.split("```")[1]
        if cypher.lower().startswith("cypher"):
            cypher = cypher[6:]
    return cypher.strip()


def _serializable(value):
    """Convierte tipos Neo4j a tipos Python serializables."""
    from neo4j.graph import Node, Relationship, Path
    if isinstance(value, (Node, Relationship)):
        return dict(value)
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, list):
        return [_serializable(v) for v in value]
    if isinstance(value, dict):
        return {k: _serializable(v) for k, v in value.items()}
    return value


def ejecutar_cypher(cypher: str) -> list[dict]:
    with driver.session() as session:
        result = session.run(cypher)
        return [
            {k: _serializable(v) for k, v in record.items()}
            for record in result
        ]


def formatear_respuesta(pregunta: str, cypher: str, datos: list[dict]) -> str:
    datos_str = json.dumps(datos, ensure_ascii=False, indent=2)
    messages = [
        SystemMessage(content=SYSTEM_RESPUESTA),
        HumanMessage(
            content=(
                f"Pregunta: {pregunta}\n\n"
                f"Query ejecutada:\n{cypher}\n\n"
                f"Resultados:\n{datos_str}"
            )
        ),
    ]
    respuesta = llm.invoke(messages)
    return respuesta.content.strip()


def corregir_cypher(cypher: str, error: str, pregunta: str) -> str:
    messages = [
        SystemMessage(content=SYSTEM_CYPHER.format(schema=GRAPH_SCHEMA)),
        HumanMessage(
            content=(
                f"Pregunta: {pregunta}\n\n"
                f"Intenté con esta query:\n{cypher}\n\n"
                f"Pero dio este error:\n{error}\n\n"
                "Genera una query Cypher corregida y más simple."
            )
        ),
    ]
    respuesta = llm.invoke(messages)
    cypher = respuesta.content.strip()
    if cypher.startswith("```"):
        cypher = cypher.split("```")[1]
        if cypher.lower().startswith("cypher"):
            cypher = cypher[6:]
    return cypher.strip()


def consultar(pregunta: str) -> str:
    print("\n[Generando query Cypher...]")
    cypher = generar_cypher(pregunta)
    print(f"  → {cypher}\n")

    if "SIN_DATOS" in cypher:
        return "No encontré información en el grafo para responder esa pregunta."

    try:
        datos = ejecutar_cypher(cypher)
    except Exception as e:
        print(f"[Error en query, reintentando...] {e}\n")
        cypher = corregir_cypher(cypher, str(e), pregunta)
        print(f"  → {cypher}\n")
        try:
            datos = ejecutar_cypher(cypher)
        except Exception as e2:
            return f"No pude ejecutar la consulta: {e2}"

    if not datos:
        return "La consulta no devolvió resultados. Puede que no haya información sobre ese tema en el grafo."

    return formatear_respuesta(pregunta, cypher, datos)


# ── CLI interactivo ─────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  Consultas al Grafo Neo4j en lenguaje natural")
    print("  Escribe 'salir' para terminar.")
    print("=" * 60)

    while True:
        try:
            pregunta = input("\n¿Qué quieres saber? → ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nHasta luego.")
            break

        if not pregunta:
            continue
        if pregunta.lower() in {"salir", "exit", "quit"}:
            print("Hasta luego.")
            break

        respuesta = consultar(pregunta)
        print("\n" + "─" * 60)
        print(respuesta)
        print("─" * 60)

    driver.close()


if __name__ == "__main__":
    main()
