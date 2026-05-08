"""Tests para casos de uso de IA (búsqueda y recomendaciones)."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.application.use_cases.ai.get_incident_recommendations import (
    GetRecommendationsRequest,
    GetRecommendationsUseCase,
)
from src.application.use_cases.ai.search_similar_incidents import (
    SearchSimilarIncidentsRequest,
    SearchSimilarIncidentsUseCase,
)
from src.domain.value_objects import IncidentCategory


@pytest.fixture
def mock_incident_repository():
    return AsyncMock()


@pytest.fixture
def mock_embedding_model():
    model = AsyncMock()
    model.generate_embedding = AsyncMock(return_value=[0.1, 0.2, 0.3])
    return model


@pytest.fixture
def mock_vector_store():
    store = AsyncMock()
    store.search_similar = AsyncMock(return_value=[])
    return store


class TestSearchSimilarIncidentsUseCase:
    """Tests para SearchSimilarIncidentsUseCase."""

    @pytest.mark.asyncio
    async def test_search_with_fallback(self, mock_incident_repository):
        """Búsqueda por palabras clave debe funcionar sin modelos."""
        mock_incident = MagicMock(
            id=uuid4(),
            ticket_number="INC-001",
            title="Server down",
            description="Database connection lost",
            priority=MagicMock(value=4),
            priority_label="Critical",
            status=MagicMock(value="resolved"),
            category=MagicMock(value="infrastructure"),
        )
        mock_incident_repository.list_all = AsyncMock(return_value=([mock_incident], 1))

        use_case = SearchSimilarIncidentsUseCase(
            incident_repository=mock_incident_repository,
        )

        results = await use_case.execute(query="server database")

        assert len(results) > 0
        assert results[0].ticket_number == "INC-001"

    @pytest.mark.asyncio
    async def test_search_with_embeddings(
        self,
        mock_incident_repository,
        mock_embedding_model,
        mock_vector_store,
    ):
        """Búsqueda con embeddings debe funcionar."""
        incident_id = uuid4()
        mock_incident = MagicMock(
            id=incident_id,
            ticket_number="INC-002",
            title="Network issue",
            description="Slow network",
            priority=MagicMock(value=3),
            priority_label="High",
            status=MagicMock(value="open"),
            category=MagicMock(value="network"),
        )
        mock_incident_repository.get_by_id = AsyncMock(return_value=mock_incident)
        mock_vector_store.search_similar = AsyncMock(return_value=[
            {"incident_id": incident_id, "score": 0.85},
        ])

        use_case = SearchSimilarIncidentsUseCase(
            incident_repository=mock_incident_repository,
            embedding_model=mock_embedding_model,
            vector_store=mock_vector_store,
        )

        results = await use_case.execute(query="network slow")

        assert len(results) == 1
        assert results[0].similarity_score == 0.85

    @pytest.mark.asyncio
    async def test_search_fallback_skips_self(self, mock_incident_repository):
        """Fallback debe saltar el incidente actual si se pasa incident_id."""
        incident_id = uuid4()
        other_id = uuid4()
        mock_self = MagicMock(
            id=incident_id, ticket_number="INC-001", title="Server down",
            description="Database connection lost", priority=MagicMock(value=4),
            priority_label="Critical", status=MagicMock(value="open"),
            category=MagicMock(value="infrastructure"),
        )
        mock_other = MagicMock(
            id=other_id, ticket_number="INC-002", title="Server issue",
            description="Database connection problem", priority=MagicMock(value=3),
            priority_label="High", status=MagicMock(value="resolved"),
            category=MagicMock(value="infrastructure"),
        )
        mock_incident_repository.list_all = AsyncMock(
            return_value=([mock_self, mock_other], 2)
        )

        use_case = SearchSimilarIncidentsUseCase(
            incident_repository=mock_incident_repository,
        )

        results = await use_case.execute(
            query="server database", incident_id=incident_id
        )

        assert len(results) == 1
        assert results[0].incident_id == other_id

    @pytest.mark.asyncio
    async def test_search_empty_results(self, mock_incident_repository):
        """Sin coincidencias debe retornar lista vacía."""
        mock_incident_repository.list_all = AsyncMock(return_value=([], 0))

        use_case = SearchSimilarIncidentsUseCase(
            incident_repository=mock_incident_repository,
        )

        results = await use_case.execute(query="xyz nonexistent")

        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_search_with_request_object(self, mock_incident_repository):
        """SearchSimilarIncidentsRequest debe funcionar."""
        mock_incident_repository.list_all = AsyncMock(return_value=([], 0))

        use_case = SearchSimilarIncidentsUseCase(
            incident_repository=mock_incident_repository,
        )

        request = SearchSimilarIncidentsRequest(query="test", limit=3)
        results = await use_case.execute(
            query=request.query,
            limit=request.limit,
        )

        assert results == []


class TestGetRecommendationsUseCase:
    """Tests para GetRecommendationsUseCase."""

    @pytest.mark.asyncio
    async def test_recommendations_with_similar(self, mock_incident_repository):
        """Con incidentes similares debe calcular prioridad."""
        incident_id = uuid4()
        mock_incident = MagicMock(
            id=incident_id,
            title="Test incident",
            description="Description",
            urgency=3,
            impact=3,
            priority=MagicMock(value=4),
            category=MagicMock(value="software"),
            status=MagicMock(value="open"),
            resolved_at=None,
            created_at=None,
        )
        mock_incident_repository.get_by_id = AsyncMock(return_value=mock_incident)

        similar_incident = MagicMock(
            id=uuid4(),
            title="Similar",
            description="Similar description",
            priority=MagicMock(value=3),
            status=MagicMock(value="resolved"),
            category=MagicMock(value="software"),
            resolved_at=None,
            created_at=None,
        )
        mock_incident_repository.list_all = AsyncMock(return_value=([similar_incident], 1))

        use_case = GetRecommendationsUseCase(
            incident_repository=mock_incident_repository,
        )

        request = GetRecommendationsRequest(incident_id=incident_id)
        result = await use_case.execute(request)

        assert result is not None
        assert result.similar_incidents_count > 0
        assert result.suggested_actions is not None

    @pytest.mark.asyncio
    async def test_recommendations_no_similar(self, mock_incident_repository):
        """Sin incidentes similares debe retornar valores por defecto."""
        incident_id = uuid4()
        mock_incident = MagicMock(
            id=incident_id,
            title="Test",
            description="Description",
            urgency=3,
            impact=3,
            priority=None,
            category=None,
            status=MagicMock(value="new"),
            resolved_at=None,
            created_at=None,
        )
        mock_incident_repository.get_by_id = AsyncMock(return_value=mock_incident)
        mock_incident_repository.list_all = AsyncMock(return_value=([], 0))

        use_case = GetRecommendationsUseCase(
            incident_repository=mock_incident_repository,
        )

        request = GetRecommendationsRequest(incident_id=incident_id)
        result = await use_case.execute(request)

        assert result is not None
        assert result.similar_incidents_count == 0

    @pytest.mark.asyncio
    async def test_recommendations_incident_not_found(self, mock_incident_repository):
        """Incidente no encontrado debe lanzar ValueError."""
        mock_incident_repository.get_by_id = AsyncMock(return_value=None)

        use_case = GetRecommendationsUseCase(
            incident_repository=mock_incident_repository,
        )

        request = GetRecommendationsRequest(incident_id=uuid4())
        with pytest.raises(ValueError, match="not found"):
            await use_case.execute(request)

    @pytest.mark.asyncio
    async def test_with_llm_explanation(self, mock_incident_repository):
        """Con LLM client debe generar explicación vía LLM."""
        incident_id = uuid4()
        mock_incident = MagicMock(
            id=incident_id, title="Test", description="Desc",
            urgency=3, impact=3, priority=MagicMock(value=3),
            category=None, status=MagicMock(value="open"),
            resolved_at=None, created_at=None,
        )
        mock_incident_repository.get_by_id = AsyncMock(return_value=mock_incident)
        mock_incident_repository.list_all = AsyncMock(return_value=([], 0))

        llm_client = MagicMock()
        llm_client.generate_explanation = AsyncMock(
            return_value="LLM generated explanation"
        )

        use_case = GetRecommendationsUseCase(
            incident_repository=mock_incident_repository,
            llm_client=llm_client,
        )

        request = GetRecommendationsRequest(
            incident_id=incident_id, include_llm_explanation=True,
        )
        result = await use_case.execute(request)

        assert result.explanation == "LLM generated explanation"
        llm_client.generate_explanation.assert_called_once()

    @pytest.mark.asyncio
    async def test_with_embeddings_and_vector_store(self, mock_incident_repository):
        """Con embedding model y vector store debe buscar por embeddings."""
        incident_id = uuid4()
        similar_id = uuid4()
        mock_incident = MagicMock(
            id=incident_id, title="Test", description="Desc",
            urgency=3, impact=3, priority=MagicMock(value=3),
            category=None, status=MagicMock(value="open"),
            resolved_at=None, created_at=None,
        )
        mock_similar = MagicMock(
            id=similar_id, title="Similar", description="Similar Desc",
            priority=MagicMock(value=4), category=None,
            status=MagicMock(value="resolved"),
            resolved_at=None, created_at=None,
        )
        mock_incident_repository.get_by_id = AsyncMock(
            side_effect=[mock_incident, mock_similar]
        )
        mock_vector_store = AsyncMock()
        mock_vector_store.search_similar = AsyncMock(return_value=[
            {"incident_id": similar_id, "score": 0.85},
        ])
        mock_embedding_model = AsyncMock()
        mock_embedding_model.generate_embedding = AsyncMock(
            return_value=[0.1, 0.2, 0.3]
        )

        use_case = GetRecommendationsUseCase(
            incident_repository=mock_incident_repository,
            embedding_model=mock_embedding_model,
            vector_store=mock_vector_store,
        )

        request = GetRecommendationsRequest(incident_id=incident_id)
        result = await use_case.execute(request)

        assert result.similar_incidents_count == 1
        mock_embedding_model.generate_embedding.assert_called_once()
        mock_vector_store.search_similar.assert_called_once()

    @pytest.mark.asyncio
    async def test_with_high_urgency_impact(self, mock_incident_repository):
        """Urgencia o impacto alto debe sugerir escalación."""
        incident_id = uuid4()
        mock_incident = MagicMock(
            id=incident_id, title="Critical", description="Emergency",
            urgency=5, impact=5, priority=None,
            category=IncidentCategory.NETWORK,
            status=MagicMock(value="new"),
            resolved_at=None, created_at=None,
        )
        mock_incident_repository.get_by_id = AsyncMock(return_value=mock_incident)
        mock_incident_repository.list_all = AsyncMock(return_value=([], 0))

        use_case = GetRecommendationsUseCase(
            incident_repository=mock_incident_repository,
        )

        request = GetRecommendationsRequest(incident_id=incident_id)
        result = await use_case.execute(request)

        assert any("escalate" in action.lower() for action in result.suggested_actions)

    @pytest.mark.asyncio
    async def test_with_multiple_resolved_similar(self, mock_incident_repository):
        """Con 3+ similares resueltos debe recomendar seguir patrón."""
        incident_id = uuid4()
        mock_incident = MagicMock(
            id=incident_id, title="Test", description="Desc",
            urgency=3, impact=3, priority=MagicMock(value=2),
            category=IncidentCategory.SOFTWARE,
            status=MagicMock(value="open"),
            resolved_at=None, created_at=None,
        )
        similar_list = []
        for i in range(5):
            inc = MagicMock(
                id=uuid4(), title=f"Similar {i}", description=f"Desc {i}",
                priority=MagicMock(value=3), category=IncidentCategory.SOFTWARE,
                status=MagicMock(value="resolved"),
                resolved_at=None, created_at=None,
            )
            similar_list.append(inc)

        mock_incident_repository.get_by_id = AsyncMock(return_value=mock_incident)
        mock_incident_repository.list_all = AsyncMock(
            return_value=(similar_list, len(similar_list))
        )

        use_case = GetRecommendationsUseCase(
            incident_repository=mock_incident_repository,
        )

        request = GetRecommendationsRequest(incident_id=incident_id)
        result = await use_case.execute(request)

        assert result.suggested_actions[0] == (
            "Consider following the resolution pattern from similar resolved incidents"
        )

    @pytest.mark.asyncio
    async def test_with_no_priorities_in_similar(self, mock_incident_repository):
        """Similares sin prioridad deben retornar valor por defecto."""
        incident_id = uuid4()
        mock_incident = MagicMock(
            id=incident_id, title="Test", description="Desc",
            urgency=3, impact=3, priority=None,
            category=None, status=MagicMock(value="new"),
            resolved_at=None, created_at=None,
        )
        similar_no_priority = MagicMock(
            id=uuid4(), title="Similar", description="Desc",
            priority=None, category=None,
            status=MagicMock(value="resolved"),
            resolved_at=None, created_at=None,
        )
        mock_incident_repository.get_by_id = AsyncMock(return_value=mock_incident)
        mock_incident_repository.list_all = AsyncMock(
            return_value=([similar_no_priority], 1)
        )

        use_case = GetRecommendationsUseCase(
            incident_repository=mock_incident_repository,
        )

        request = GetRecommendationsRequest(incident_id=incident_id)
        result = await use_case.execute(request)

        assert result.recommended_priority == 3
        assert result.confidence == 0.5

    @pytest.mark.asyncio
    async def test_with_resolved_time_calculation(self, mock_incident_repository):
        """Similares resueltos con fechas deben calcular tiempo promedio."""
        incident_id = uuid4()
        now = datetime.now(UTC)
        mock_incident = MagicMock(
            id=incident_id, title="Test", description="Desc",
            urgency=3, impact=3, priority=MagicMock(value=3),
            category=None, status=MagicMock(value="open"),
            resolved_at=None, created_at=None,
        )
        resolved_inc = MagicMock(
            id=uuid4(), title="Resolved", description="Desc",
            priority=MagicMock(value=2), category=None,
            status=MagicMock(value="resolved"),
            resolved_at=now, created_at=now,
        )
        mock_incident_repository.get_by_id = AsyncMock(return_value=mock_incident)
        mock_incident_repository.list_all = AsyncMock(
            return_value=([resolved_inc], 1)
        )

        use_case = GetRecommendationsUseCase(
            incident_repository=mock_incident_repository,
        )

        request = GetRecommendationsRequest(incident_id=incident_id)
        result = await use_case.execute(request)

        assert result.avg_resolution_time_hours == 0.0

    @pytest.mark.asyncio
    async def test_llm_explanation_error(self, mock_incident_repository):
        """Error en LLM debe caer a explicación por defecto."""
        incident_id = uuid4()
        mock_incident = MagicMock(
            id=incident_id, title="Test", description="Desc",
            urgency=3, impact=3, priority=MagicMock(value=3),
            category=None, status=MagicMock(value="open"),
            resolved_at=None, created_at=None,
        )
        mock_incident_repository.get_by_id = AsyncMock(return_value=mock_incident)
        mock_incident_repository.list_all = AsyncMock(return_value=([], 0))

        llm_client = MagicMock()
        llm_client.generate_explanation = AsyncMock(
            side_effect=Exception("LLM failure")
        )

        use_case = GetRecommendationsUseCase(
            incident_repository=mock_incident_repository,
            llm_client=llm_client,
        )

        request = GetRecommendationsRequest(
            incident_id=incident_id, include_llm_explanation=True,
        )
        result = await use_case.execute(request)

        assert "default" not in result.explanation.lower()

    @pytest.mark.asyncio
    async def test_category_match_in_actions(self, mock_incident_repository):
        """Categoría coincidente debe sugerir procedimiento estándar."""
        incident_id = uuid4()
        similar_id = uuid4()
        mock_incident = MagicMock(
            id=incident_id, title="Test", description="Desc",
            urgency=3, impact=3, priority=MagicMock(value=2),
            category=IncidentCategory.SOFTWARE,
            status=MagicMock(value="open"),
            resolved_at=None, created_at=None,
        )
        mock_similar = MagicMock(
            id=similar_id, title="Similar", description="Desc",
            priority=MagicMock(value=3), category=IncidentCategory.SOFTWARE,
            status=MagicMock(value="resolved"),
            resolved_at=None, created_at=None,
        )
        mock_incident_repository.get_by_id = AsyncMock(return_value=mock_incident)
        mock_incident_repository.list_all = AsyncMock(
            return_value=([mock_similar], 1)
        )

        use_case = GetRecommendationsUseCase(
            incident_repository=mock_incident_repository,
        )

        request = GetRecommendationsRequest(incident_id=incident_id)
        result = await use_case.execute(request)

        category_actions = [
            a for a in result.suggested_actions
            if "category matches" in a.lower()
        ]
        assert len(category_actions) > 0

    @pytest.mark.asyncio
    async def test_fallback_skips_self_in_similar(self, mock_incident_repository):
        """Fallback de _find_similar_incidents debe saltar el incidente actual."""
        incident_id = uuid4()
        other_id = uuid4()
        mock_incident = MagicMock(
            id=incident_id, title="Test incident", description="Desc",
            urgency=3, impact=3, priority=MagicMock(value=2),
            category=None, status=MagicMock(value="open"),
            resolved_at=None, created_at=None,
        )
        mock_other = MagicMock(
            id=other_id, title="Other similar", description="Desc",
            priority=MagicMock(value=3), category=None,
            status=MagicMock(value="resolved"),
            resolved_at=None, created_at=None,
        )
        mock_incident_repository.get_by_id = AsyncMock(return_value=mock_incident)
        mock_incident_repository.list_all = AsyncMock(
            return_value=([mock_incident, mock_other], 2)
        )

        use_case = GetRecommendationsUseCase(
            incident_repository=mock_incident_repository,
        )

        request = GetRecommendationsRequest(incident_id=incident_id)
        result = await use_case.execute(request)

        assert result.similar_incidents_count == 1
