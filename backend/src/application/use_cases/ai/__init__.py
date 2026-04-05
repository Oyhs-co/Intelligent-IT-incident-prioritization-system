"""Use cases para similitud y búsqueda de incidentes."""

from .search_similar_incidents import (
    SearchSimilarIncidentsRequest,
    SearchSimilarIncidentsUseCase,
    SimilarIncidentResult,
)
from .get_incident_recommendations import (
    GetRecommendationsRequest,
    GetRecommendationsUseCase,
    RecommendationResult,
)

__all__ = [
    "SearchSimilarIncidentsRequest",
    "SearchSimilarIncidentsUseCase",
    "SimilarIncidentResult",
    "GetRecommendationsRequest",
    "GetRecommendationsUseCase",
    "RecommendationResult",
]
