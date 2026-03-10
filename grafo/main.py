from langchain_core.language_models.chat_models import BaseChatModel
from neo4j import GraphDatabase
from langchain_core.messages import SystemMessage, HumanMessage
from .prompts import SYSTEM_ENTITY_RELATIONSHIP_EXTRACTION_PROMPT_1, HUMAN_ENTITY_RELATIONSHIP_EXTRACTION_PROMPT_1
from langchain_core.output_parsers import JsonOutputParser

parser = JsonOutputParser()

# Crea un node del grafo
def create_entity(label: str):
    query = f"""
MERGE (e:{label} {{name: $name}})
SET e.description = $description
"""
    return query


# Crea una arista del grafo
def create_relationship(rel_type: str):
    query = f"""
MATCH (a {{name: $source}})
MATCH (b {{name: $target}})
MERGE (a)-[r:{rel_type}]->(b)
SET r.description = $description
"""
    return query




def make_graph_collection(chunk_content : str, llm : BaseChatModel) -> bool:
    
    URI = "bolt://localhost:7687"
    USER = "neo4j"
    PASSWORD = "dulcinea2000."
    AUTH = (URI, USER, PASSWORD)

    driver = GraphDatabase.driver(uri=URI, auth=(USER, PASSWORD))


    messages = [
                    SystemMessage(content=SYSTEM_ENTITY_RELATIONSHIP_EXTRACTION_PROMPT_1),
                    HumanMessage(content=HUMAN_ENTITY_RELATIONSHIP_EXTRACTION_PROMPT_1.format(text=chunk_content))
                ]
    try:
        ai_message = llm.invoke(messages)
        json_res = parser.parse(ai_message.content)
        print(f"{ai_message.pretty_repr()}")
        print(f"\n\n input_tokens: {ai_message.usage_metadata['input_tokens']}, output_tokens: {ai_message.usage_metadata['output_tokens']} \n\n")
        print("Entidades y relaciones extraidas del chunk \n")

        


        entities_list = json_res["entities"]
        for i, entity in enumerate(entities_list):
            query = create_entity(label=entity["entity_type"])

            with driver.session() as neo_session:
                    neo_session.run(
                        query,
                        name=entity["entity_name"],
                        description=entity["entity_description"]
                                    )
            print("Entidades extraidas y guardadas con exito")
        print("\n\n")
        

        relations_list = json_res["relationships"]
        for i, relation in enumerate(relations_list):
            query = create_relationship(rel_type=relation["relationship_type"])
            with driver.session() as neo_session:
                    neo_session.run(
                    query,
                    source=relation["source_entity"],
                    target=relation["target_entity"],
                    description=relation["relationship_description"]
                    )
            print("Relaciones extraidas y guardadas con exito")
        
        driver.close()
        print("\n"*5)
        return True
    except Exception as e:
         print(f"Error: {e}")
         print("\n"*5)
         return False


if __name__=="__main__":
    from pathlib import Path
    from dotenv import load_dotenv
    from langchain_groq import ChatGroq
    from langchain_google_genai import ChatGoogleGenerativeAI
    import time
    import os
    import re

    load_dotenv()
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

    # model = "openai/gpt-oss-120b"
    # llm = ChatGroq(model=model, temperature=0.1, api_key=GROQ_API_KEY)


    model = "gemini-2.0-flash"
    llm = ChatGoogleGenerativeAI(model=model, temperature=0.5, google_api_key=GOOGLE_API_KEY)

    root = Path(__file__).resolve().parent.parent
    ruta = root / "_docs" / "graphdata"


    # Obtener archivos y ordenarlos por el número en el nombre
    archivos = sorted(
        ruta.glob("discord_chanel_*.txt"),
        key=lambda x: int(re.search(r"\d+", x.stem).group())
    )

    n = 0
    l = []
    for archivo in archivos:
        with open(archivo, "r", encoding="utf-8") as f:
            contenido = f.read()
            x = make_graph_collection(chunk_content=contenido, llm=llm)
            if not x:
                 l.append(n)
            n += 1
            time.sleep(1)
        
        #print(f"\n===== {archivo.name} =====")



"""
python3 -m grafo.main

"""