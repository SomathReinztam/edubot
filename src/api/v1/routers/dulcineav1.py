from pydantic import BaseModel
from typing import Literal

from src.apps.Dulcinea.main import get_dulci_report
from fastapi import APIRouter

router = APIRouter(prefix="dulciv1", tags=["Dulci"])

class Dulcinea(BaseModel):
    query : str
    guild_name : Literal["Unergy", "The_Sun_Factory"]
    channel_name : str


class DulcineaResponse(BaseModel):
    result : str


@router.post("/", response_model=DulcineaResponse)
async def get_dulci_report_api(body : Dulcinea):
    result = get_dulci_report(query=body.query, guild_name=body.guild_name, channel_name=body.channel_name)
    return DulcineaResponse(result=result)

