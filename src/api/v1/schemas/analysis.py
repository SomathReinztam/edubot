from pydantic import BaseModel, Field
from typing import Literal, Optional, Union, Annotated


class ModelProviderBase(BaseModel):
    temperature: float
    api_key: str


class GoogleModel(ModelProviderBase):
    client: Literal["google"]
    model: Literal[
        "gemini-2.0-flash",
        "gemini-2.5-flash",
        "gemini-2.5-pro",
        "gemini-3-flash-preview",
        "gemini-3.1-flash-lite-preview",
        "gemini-3.1-pro-preview"
    ]


class GroqModels(ModelProviderBase):
    client: Literal["groq"]
    model: Literal[
        "llama-3.3-70b-versatile",
        "openai/gpt-oss-120b",
        "moonshotai/kimi-k2-instruct-0905"
    ]


class DeepSeekModels(ModelProviderBase):
    client: Literal["deepseek"]
    model: Literal[
        "deepseek-chat",
        "deepseek-reasoner"
    ]


ModelProvider = Annotated[
    Union[GoogleModel, GroqModels, DeepSeekModels],
    Field(discriminator="client")
]


class Analysis(BaseModel):
    user_id: int
    query: str
    top_n: int 

    model_analyst: ModelProvider
    model_querier: ModelProvider
    model_halting: ModelProvider


class AnalysisResponse(BaseModel):
    analysis_id: int
    query: str
    analysis: str
    created_at: str


class AnalysisSummary(BaseModel):
    analysis_id: int
    query: str
    created_at: str


class AnalysisListResponse(BaseModel):
    analyses: list[AnalysisSummary]