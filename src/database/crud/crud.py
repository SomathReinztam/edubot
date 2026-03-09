from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from contextlib import contextmanager
from typing import Dict, Optional, List, Any
from datetime import datetime
from src.database import models
from src.utils import settings

from src.database.crud import schema 




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
    


    def new_user(self, name : str, email : str, password : str):
                with self.session_scope() as session:

                    user_db = models.AppUserModel(
                        name=name,
                        email=email,
                        password=password
                    )
                
                    session.add(user_db)
                    session.flush()
    

    def make_analysis(self, user_id : int, model_analyst : schema.ModelProvider, model_querier : schema.ModelProvider, model_halting : schema.ModelProvider, query : str) -> str:
         pass
    

    

if __name__=="__main__":
     crudhelper = CrudHelper()
     crudhelper.create_database()

"""
python3 -m src.database.crud.crud

"""