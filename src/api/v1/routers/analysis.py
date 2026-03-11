from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from src.database.crud.crud import CrudHelper
from ..schemas.analysis import Analysis

router = APIRouter(prefix="/edubot/analyze", tags=["Analysis"])

# Función generadora para la dependencia
def get_crud_helper():
    return CrudHelper()

# CORRECCIÓN: Usamos response_class en lugar de response_model
@router.post("/", response_class=StreamingResponse)
async def analyze_streaming(body: Analysis, crud: CrudHelper = Depends(get_crud_helper)):
    
    # crud.stream_edubot_analysis (que me mostraste en el mensaje anterior) 
    # ya hace los 'yield' necesarios.
    result_generator = crud.stream_edubot_analysis(
        user_id=body.user_id, 
        model_analyst=body.model_analyst.model_dump(),
        model_querier=body.model_querier.model_dump(),
        model_halting=body.model_halting.model_dump(),
        query=body.query,
        top_n=body.top_n
    )
    
    # Retornamos el StreamingResponse con el generador
    return StreamingResponse(result_generator, media_type="text/event-stream")