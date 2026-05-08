"""Ports (interfaces) de la capa de aplicación."""

from .i_ai_model import IAIModel
from .i_embedding_model import IEmbeddingModel
from .i_llm_client import ILLMClient
from .i_notification_channel import INotificationChannel

__all__ = [
    "IAIModel",
    "ILLMClient",
    "INotificationChannel",
    "IEmbeddingModel",
]
