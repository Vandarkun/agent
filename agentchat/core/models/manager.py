from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI

from agentchat.settings import app_settings


class ModelManager:
    """Thin factory for the chat models used by the agents and tools."""

    @classmethod
    def get_tool_invocation_model(cls, **kwargs) -> BaseChatModel:
        return ChatOpenAI(
            model=app_settings.multi_models.tool_call_model.model_name,
            api_key=app_settings.multi_models.tool_call_model.api_key,
            base_url=app_settings.multi_models.tool_call_model.base_url,
        )

    @classmethod
    def get_conversation_model(cls, **kwargs) -> BaseChatModel:
        return ChatOpenAI(
            model=app_settings.multi_models.conversation_model.model_name,
            api_key=app_settings.multi_models.conversation_model.api_key,
            base_url=app_settings.multi_models.conversation_model.base_url,
        )
