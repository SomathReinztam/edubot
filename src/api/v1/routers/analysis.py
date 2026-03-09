from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from src.database.crud.crud import CrudHelper
from src.database.crud.schema import DatabaseError
from ..schemas.analysis import Analysis, AnalysisResponse, AnalysisSummary, AnalysisListResponse
import asyncio
import json
from concurrent.futures import ThreadPoolExecutor

_executor = ThreadPoolExecutor(max_workers=4)

router = APIRouter(prefix="/analysis", tags=["Analysis"])
crud = CrudHelper()


@router.post("/", response_model=AnalysisResponse)
async def make_analysis_api(body: Analysis):
    result = crud.make_edubot_analysis(
        user_id=body.user_id,
        model_analyst=body.model_analyst.model_dump(),
        model_querier=body.model_querier.model_dump(),
        model_halting=body.model_halting.model_dump(),
        query=body.query,
        top_n=body.top_n,
    )
    return AnalysisResponse(**result)


@router.get("/user/{user_id}", response_model=AnalysisListResponse)
async def get_user_analyses_api(user_id: int):
    analyses = crud.get_user_analyses(user_id=user_id)
    return AnalysisListResponse(analyses=[AnalysisSummary(**a) for a in analyses])


@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis_api(analysis_id: int):
    try:
        result = crud.get_analysis(analysis_id=analysis_id)
        return AnalysisResponse(**result)
    except DatabaseError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/stream")
async def stream_analysis_api(body: Analysis):
    loop = asyncio.get_running_loop()
    queue: asyncio.Queue = asyncio.Queue()

    def run_agent():
        try:
            for event in crud.iter_edubot_analysis_events(
                user_id=body.user_id,
                model_analyst=body.model_analyst.model_dump(),
                model_querier=body.model_querier.model_dump(),
                model_halting=body.model_halting.model_dump(),
                query=body.query,
                top_n=body.top_n,
            ):
                asyncio.run_coroutine_threadsafe(queue.put(event), loop).result()
        except Exception as e:
            asyncio.run_coroutine_threadsafe(
                queue.put({"type": "error", "data": {"message": str(e)}}), loop
            ).result()
        finally:
            asyncio.run_coroutine_threadsafe(queue.put(None), loop).result()

    async def generate():
        loop.run_in_executor(_executor, run_agent)
        while True:
            event = await queue.get()
            if event is None:
                break
            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.delete("/{analysis_id}")
async def delete_analysis_api(analysis_id: int):
    try:
        crud.delete_analysis(analysis_id=analysis_id)
        return {"message": "Análisis eliminado"}
    except DatabaseError as e:
        raise HTTPException(status_code=404, detail=str(e))
