from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String, JSON, DateTime, func, ForeignKey, Text
from sqlalchemy.orm import relationship


class Base(DeclarativeBase):
    pass


class AppUserModel(Base):
    __tablename__ = "appusers"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    email = Column(String)
    password = Column(String)
    


class AnalysisModel(Base):
    analysis_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("appusers.user_id"), nullable=False)

    # par los model analyst, querier, halting un ejmplo de json esperado es : {"client":google, "model":"gemini-2.0-flash", "temperature":0.2, "api_key":"abc123", "base_url:"http://localhost:11434/"}
    model_analyst = Column(JSON) 
    model_querier = Column(JSON)
    model_halting = Column(JSON)

    query = Column(Text)
    analysis = Column(Text)

    user = relationship("AppUserModel", backref="analysis")



