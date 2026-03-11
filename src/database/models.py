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

    query = Column(Text)
    analysis = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("AppUserModel", backref="analysis")



