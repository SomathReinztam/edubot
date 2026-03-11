from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from src.database.crud.crud import CrudHelper
from src.database.crud.schema import DatabaseError
from ..schemas.analysis import Analysis
from typing import List

router = APIRouter(prefix="/edubot/analyze", tags=["Analysis"])

def get_crud_helper():
    return CrudHelper()

@router.post("/", response_class=StreamingResponse)
async def analyze_streaming(body: Analysis, crud: CrudHelper = Depends(get_crud_helper)):
    result_generator = crud.stream_edubot_analysis(
        user_id=body.user_id,
        model_analyst=body.model_analyst.model_dump(),
        model_querier=body.model_querier.model_dump(),
        model_halting=body.model_halting.model_dump(),
        query=body.query,
        top_n=body.top_n
    )
    return StreamingResponse(result_generator, media_type="text/event-stream")


@router.get("/user/{user_id}")
async def get_user_analyses(user_id: int, crud: CrudHelper = Depends(get_crud_helper)):
    return crud.get_user_analyses(user_id=user_id)


@router.get("/{analysis_id}")
async def get_analysis(analysis_id: int, crud: CrudHelper = Depends(get_crud_helper)):
    try:
        return crud.get_analysis(analysis_id=analysis_id)
    except DatabaseError as e:
        raise HTTPException(status_code=404, detail=str(e))