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
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from src.analyst.prompts import analyst
from src.analyst.prompts.edubotdb import DB_SKILL_1
import json


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
            raise schema.DatabaseError(
                f"No se pudo crear la base de datos: {str(e)}"
            ) from e

    def new_user(self, name: str, email: str, password: str):
        with self.session_scope() as session:
            user_db = models.AppUserModel(name=name, email=email, password=password)

            session.add(user_db)
            session.flush()

    def get_user(self, user_id: int) -> Optional[Dict]:
        with self.session_scope() as session:
            user = (
                session.query(models.AppUserModel)
                .filter(models.AppUserModel.user_id == user_id)
                .first()
            )
            if not user:
                raise schema.UserNotFoundError(f"Usuario {user_id} no encontrado")
            return {"user_id": user.user_id, "name": user.name, "email": user.email}

    def login(self, email: str, password: str) -> Dict:
        with self.session_scope() as session:
            user = (
                session.query(models.AppUserModel)
                .filter(
                    models.AppUserModel.email == email,
                    models.AppUserModel.password == password,
                )
                .first()
            )
            if not user:
                raise schema.UserNotFoundError("Email o contraseña incorrectos")
            return {"user_id": user.user_id, "name": user.name, "email": user.email}

    def _get_langchain_model(self, model_provider: Dict[str, Any]) -> BaseChatModel:
        client = model_provider["client"]

        if client == "google":
            from langchain_google_genai import ChatGoogleGenerativeAI

            chat_model = ChatGoogleGenerativeAI(
                model=model_provider["model"],
                temperature=model_provider["temperature"],
                google_api_key=model_provider["api_key"],
            )
            return chat_model
        if client == "groq":
            from langchain_groq import ChatGroq

            chat_model = ChatGroq(
                model=model_provider["model"],
                temperature=model_provider["temperature"],
                api_key=model_provider["api_key"],
            )
            return chat_model
        if client == "deepseek":
            from langchain_deepseek import ChatDeepSeek

            chat_model = ChatDeepSeek(
                model=model_provider["model"],
                temperature=model_provider["temperature"],
                api_key=model_provider["api_key"],
            )
            return chat_model

    def stream_edubot_analysis(
        self,
        user_id: int,
        model_analyst: Dict[str, Any],
        model_querier: Dict[str, Any],
        model_halting: Dict[str, Any],
        query: str,
        top_n: int,
    ):
        # ... Configuración inicial de BD, LLMs, agents (igual que en tu código original) ...
        conn_string = f"postgresql+psycopg2://{settings.EDUBOTDB_USER}:{settings.EDUBOTDB_PASS}@{settings.EDUBOTDB_HOST}:{settings.EDUBOTDB_PORT}/{settings.EDUBOTDB_NAME}"
        engine = create_engine(conn_string)

        llm_analyst = self._get_langchain_model(model_provider=model_analyst)
        llm_querier = self._get_langchain_model(model_provider=model_querier)
        llm_halting = self._get_langchain_model(model_provider=model_halting)

        messages = [
            SystemMessage(
                content=analyst.SYSTEM_DEEP_QUERIES_PROMPT_3.format(
                    topic=query, plan=DB_SKILL_1
                )
            ),
            HumanMessage(
                content=analyst.HUMAN_DEEP_QUERIES_PROMPT_2.format(topic=query)
            ),
        ]

        analyst_agent = create_analyst_agent(
            llm_analyst=llm_analyst,
            llm_querier=llm_querier,
            llm_halting=llm_halting,
            engine=engine,
            top_n=top_n,
        )
        initial_state = {"messages_analyst": messages}

        # --- INICIO DEL STREAMING ---
        for event in analyst_agent.stream(initial_state, stream_mode="values"):
            final_state = event
            msg = event["messages_analyst"][-1]

            # Preparamos el payload del evento
            step_data = {"type": "reasoning", "role": "", "content": ""}

            if isinstance(msg, HumanMessage):
                step_data["role"] = "Asistente del analista"
                step_data["content"] = (
                    msg.content if isinstance(msg.content, str) else str(msg.content)
                )
            elif isinstance(msg, AIMessage):
                step_data["role"] = "Analista"
                # Usamos pretty_repr() u otra propiedad si quieres incluir llamadas a herramientas
                step_data["content"] = (
                    msg.content if msg.content else "Procesando herramienta..."
                )

            # YIELD: Enviamos el chunk de razonamiento al cliente en formato SSE (Server-Sent Event)
            yield f"data: {json.dumps(step_data)}\n\n"

        # --- FIN DEL STREAMING: GUARDAR EN BD Y ENVIAR RESPUESTA FINAL ---
        messages_analyst = final_state["messages_analyst"]
        analysis = messages_analyst[-1].content

        # Guardado en base de datos
        with self.session_scope() as session:
            analyst_db = models.AnalysisModel(
                user_id=user_id, query=query, analysis=analysis
            )
            session.add(analyst_db)
            session.flush()

        # Emitimos el resultado final
        final_data = {"type": "final_analysis", "content": analysis}
        yield f"data: {json.dumps(final_data)}\n\n"

    def get_analysis(self, analysis_id: int) -> Dict:
        with self.session_scope() as session:
            record = (
                session.query(models.AnalysisModel)
                .filter(models.AnalysisModel.analysis_id == analysis_id)
                .first()
            )
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
            records = (
                session.query(models.AnalysisModel)
                .filter(models.AnalysisModel.user_id == user_id)
                .order_by(models.AnalysisModel.created_at.desc())
                .all()
            )
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
            record = (
                session.query(models.AnalysisModel)
                .filter(models.AnalysisModel.analysis_id == analysis_id)
                .first()
            )
            if not record:
                raise schema.DatabaseError(f"Análisis {analysis_id} no encontrado")
            session.delete(record)


if __name__ == "__main__":
    crudhelper = CrudHelper()
    crudhelper.create_database()

"""
python3 -m src.database.crud.crud

"""
