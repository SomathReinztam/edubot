from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from contextlib import contextmanager
from typing import Dict, Optional, List, Any
from datetime import datetime
from src.database import models
from src.utils import settings

from src.database.crud import schema 
from src.analyst.graphs.create_analyst_agent import create_analyst_agent

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import SystemMessage, HumanMessage
from src.analyst.prompts import analyst
from src.analyst.prompts.edubotdb import DB_SKILL_1




class CrudHelper:
    def __init__(self):
        self.conn_string = f"postgresql+psycopg2://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
        self.engine = create_engine(self.conn_string)
    
    @contextmanager
    def session_scope(self):
        """
        Context manager para manejar sesiones de base de datos de forma segura
        """
        Session = sessionmaker(bind=self.engine)
        session = Session()
        try:
            yield session
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            raise schema.DatabaseError(f"Error en base de datos: {str(e)}") from e
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()


    def create_database(self) -> None:
        """
        Crea todas las tablas en la base de datos
        """
        try:
            models.Base.metadata.create_all(self.engine)
        except SQLAlchemyError as e:
            raise schema.DatabaseError(f"No se pudo crear la base de datos: {str(e)}") from e
    


    def new_user(self, name: str, email: str, password: str):
        with self.session_scope() as session:
            user_db = models.AppUserModel(name=name, email=email, password=password)
            session.add(user_db)
            session.flush()

    def get_user(self, user_id: int) -> Optional[Dict]:
        with self.session_scope() as session:
            user = session.query(models.AppUserModel).filter(
                models.AppUserModel.user_id == user_id
            ).first()
            if not user:
                raise schema.UserNotFoundError(f"Usuario {user_id} no encontrado")
            return {"user_id": user.user_id, "name": user.name, "email": user.email}

    def login(self, email: str, password: str) -> Dict:
        with self.session_scope() as session:
            user = session.query(models.AppUserModel).filter(
                models.AppUserModel.email == email,
                models.AppUserModel.password == password
            ).first()
            if not user:
                raise schema.UserNotFoundError("Email o contraseña incorrectos")
            return {"user_id": user.user_id, "name": user.name, "email": user.email}
    

    def _get_langchain_model(self, model_provider : schema.ModelProvider) -> BaseChatModel:
         client = model_provider["client"]

         if client == "google":
              from langchain_google_genai import ChatGoogleGenerativeAI
              chat_model = ChatGoogleGenerativeAI(model=model_provider["model"], temperature=model_provider["temperature"], google_api_key=model_provider["api_key"])
              return chat_model
         if client == "groq":
              from langchain_groq import ChatGroq
              chat_model = ChatGroq(model=model_provider["model"], temperature=model_provider["temperature"], api_key=model_provider["api_key"])
              return chat_model
         if client == "deepseek":
              from langchain_deepseek import ChatDeepSeek
              chat_model = ChatDeepSeek(model=model_provider["model"], temperature=model_provider["temperature"], api_key=model_provider["api_key"])
              return chat_model
    



    def make_edubot_analysis(self, user_id: int, model_analyst: schema.ModelProvider, model_querier: schema.ModelProvider, model_halting: schema.ModelProvider, query: str, top_n: int) -> Dict:
        result = None
        for event in self.iter_edubot_analysis_events(
            user_id=user_id,
            model_analyst=model_analyst,
            model_querier=model_querier,
            model_halting=model_halting,
            query=query,
            top_n=top_n,
        ):
            if event["type"] == "complete":
                result = event["data"]
        return result

    def _extract_messages(self, msgs) -> list:
        from langchain_core.messages import RemoveMessage
        if not isinstance(msgs, list):
            msgs = [msgs]
        result = []
        for msg in msgs:
            if isinstance(msg, RemoveMessage):
                continue
            data = {"type": type(msg).__name__, "content": msg.content}
            tool_calls = getattr(msg, "tool_calls", None)
            if tool_calls:
                data["tool_calls"] = [
                    {"name": tc["name"], "args": str(tc["args"])[:300]}
                    for tc in tool_calls
                ]
            name = getattr(msg, "name", None)
            if name:
                data["tool_name"] = name
            result.append(data)
        return result

    def iter_edubot_analysis_events(self, user_id: int, model_analyst, model_querier, model_halting, query: str, top_n: int):
        conn_string = f"postgresql+psycopg2://{settings.EDUBOTDB_USER}:{settings.EDUBOTDB_PASS}@{settings.EDUBOTDB_HOST}:{settings.EDUBOTDB_PORT}/{settings.EDUBOTDB_NAME}"
        engine = create_engine(conn_string)

        llm_analyst = self._get_langchain_model(model_provider=model_analyst)
        llm_querier = self._get_langchain_model(model_provider=model_querier)
        llm_halting = self._get_langchain_model(model_provider=model_halting)

        messages = [
            SystemMessage(content=analyst.SYSTEM_DEEP_QUERIES_PROMPT_3.format(topic=query, plan=DB_SKILL_1)),
            HumanMessage(content=analyst.HUMAN_DEEP_QUERIES_PROMPT_2.format(topic=query))
        ]

        agent = create_analyst_agent(llm_analyst=llm_analyst, llm_querier=llm_querier, llm_halting=llm_halting, engine=engine, top_n=top_n)

        NODE_LABELS = {
            "initial_deep_query_node": "Analista — consulta inicial",
            "set_ReAct_messages_node": "Preparando agente SQL",
            "querier_ReAct_node": "Agente SQL procesando",
            "tool_node_wrapper": "Ejecutando herramienta SQL",
            "clear_ReAct_messages_node": "Enviando resultado al analista",
            "deep_query_node": "Analista — analizando respuesta",
            "should_end_node": "¿Análisis completo?",
        }

        final_content = None

        for chunk in agent.stream({"messages_analyst": messages}):
            for node_name, state_update in chunk.items():
                data = {}

                if "input_tokens" in state_update:
                    data["input_tokens"] = state_update["input_tokens"]
                    data["output_tokens"] = state_update.get("output_tokens", 0)
                    data["api_calls"] = state_update.get("api_calls", 0)

                if "messages_analyst" in state_update:
                    msgs = self._extract_messages(state_update["messages_analyst"])
                    if msgs:
                        data["analyst_messages"] = msgs
                        if node_name in ("initial_deep_query_node", "deep_query_node"):
                            final_content = msgs[-1]["content"]

                if "messages_ReAct" in state_update:
                    msgs = self._extract_messages(state_update["messages_ReAct"])
                    if msgs:
                        data["react_messages"] = msgs

                if "should_end" in state_update:
                    data["should_end"] = state_update["should_end"]

                yield {
                    "type": "node_update",
                    "node": node_name,
                    "label": NODE_LABELS.get(node_name, node_name),
                    "data": data,
                }

        if final_content:
            with self.session_scope() as session:
                record = models.AnalysisModel(user_id=user_id, query=query, analysis=final_content)
                session.add(record)
                session.flush()
                session.refresh(record)
                yield {
                    "type": "complete",
                    "data": {
                        "analysis_id": record.analysis_id,
                        "query": record.query,
                        "analysis": record.analysis,
                        "created_at": str(record.created_at),
                    },
                }

    def get_analysis(self, analysis_id: int) -> Dict:
        with self.session_scope() as session:
            record = session.query(models.AnalysisModel).filter(
                models.AnalysisModel.analysis_id == analysis_id
            ).first()
            if not record:
                raise schema.DatabaseError(f"Análisis {analysis_id} no encontrado")
            return {
                "analysis_id": record.analysis_id,
                "query": record.query,
                "analysis": record.analysis,
                "created_at": str(record.created_at),
            }

    def get_user_analyses(self, user_id: int) -> List[Dict]:
        with self.session_scope() as session:
            records = session.query(models.AnalysisModel).filter(
                models.AnalysisModel.user_id == user_id
            ).order_by(models.AnalysisModel.created_at.desc()).all()
            return [
                {
                    "analysis_id": r.analysis_id,
                    "query": r.query,
                    "created_at": str(r.created_at),
                }
                for r in records
            ]

    def delete_analysis(self, analysis_id: int) -> None:
        with self.session_scope() as session:
            record = session.query(models.AnalysisModel).filter(
                models.AnalysisModel.analysis_id == analysis_id
            ).first()
            if not record:
                raise schema.DatabaseError(f"Análisis {analysis_id} no encontrado")
            session.delete(record)





    

if __name__=="__main__":
     crudhelper = CrudHelper()
     crudhelper.create_database()

"""
python3 -m src.database.crud.crud

"""