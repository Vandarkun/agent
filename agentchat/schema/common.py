from pydantic import BaseModel, Field


class ModelConfig(BaseModel):
    model_name: str = ""
    api_key: str = ""
    base_url: str = ""


class MultiModels(BaseModel):
    """Minimal model settings needed by the agents and tools."""

    class Config:
        extra = "allow"

    conversation_model: ModelConfig = Field(default_factory=ModelConfig)
    tool_call_model: ModelConfig = Field(default_factory=ModelConfig)


class Tools(BaseModel):
    """API keys and endpoints for bundled tools."""

    class Config:
        extra = "allow"

    weather: dict = Field(default_factory=dict)
    bocha: dict = Field(default_factory=dict)
    delivery: dict = Field(default_factory=dict)
