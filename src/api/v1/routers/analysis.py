from fastapi import APIRouter
from src.database.crud.crud import CrudHelper
from ..schemas.analysis import Analysis, AnalysisResponse

crud = CrudHelper()
router = APIRouter(prefix="/analysis", tags=["Analysis"])

@router.post("/", response_model=AnalysisResponse)
async def make_edubot_analysis_api(body : Analysis):
    result = crud.make_edubot_analysis(
        user_id=body.user_id, 
        model_analyst=body.model_analyst.model_dump(),
        model_querier=body.model_querier.model_dump(),
        model_halting=body.model_halting.model_dump(),
        query=body.query,
        top_n=body.top_n
    )
    return AnalysisResponse(analysis=result['analysis'])
