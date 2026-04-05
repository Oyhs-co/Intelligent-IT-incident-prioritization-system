"""Conectores externos para integración con sistemas de tickets."""

from .base_connector import BaseTicketConnector, TicketConnectionError, TicketSyncError
from .jira_connector import JiraConnector
from .servicenow_connector import ServiceNowConnector

__all__ = [
    "BaseTicketConnector",
    "TicketConnectionError",
    "TicketSyncError",
    "JiraConnector",
    "ServiceNowConnector",
]
