"""Use cases para similitud y búsqueda de incidentes."""

from .get_incident_recommendations import (
    GetRecommendationsRequest,
    GetRecommendationsUseCase,
    RecommendationResult,
)
from .search_similar_incidents import (
    SearchSimilarIncidentsRequest,
    SearchSimilarIncidentsUseCase,
    SimilarIncidentResult,
)

__all__ = [
    "SearchSimilarIncidentsRequest",
    "SearchSimilarIncidentsUseCase",
    "SimilarIncidentResult",
    "GetRecommendationsRequest",
    "GetRecommendationsUseCase",
    "RecommendationResult",
]
