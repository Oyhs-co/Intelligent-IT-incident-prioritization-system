"""Ports (interfaces) de la capa de aplicación."""

from .i_ai_model import IAIModel
from .i_llm_client import ILLMClient
from .i_notification_channel import INotificationChannel
from .i_embedding_model import IEmbeddingModel

__all__ = [
    "IAIModel",
    "ILLMClient",
    "INotificationChannel",
    "IEmbeddingModel",
]
