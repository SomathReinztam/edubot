from pydantic import BaseModel
from typing import Literal, Dict, Any, Union, List, TypedDict


# ------------------------
# ------------------------


class DatabaseError(Exception):
    """Excepción base para errores de base de datos"""
    pass


class UserNotFoundError(DatabaseError):
    """Excepción cuando no se encuentra un usuario"""
    pass


class ChatNotFoundError(DatabaseError):
    """Excepción cuando no se encuentra un chat"""
    pass


# ------------------------
# ------------------------


class ModelProvider(TypedDict):
    client : str
    model : str
    temperature : float
    api_key : str
    base_url : str
