"""Tests unitarios para IncidentVectorStore."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import numpy as np
import pytest

from src.infrastructure.ml.vector_store import IncidentVectorStore, INDEX_KEY, DATA_KEY


@pytest.fixture
def store():
    return IncidentVectorStore(embedding_dim=384, host="localhost", port=6379, db=1)


class TestIncidentVectorStore:
    """Tests para IncidentVectorStore."""

    @pytest.mark.asyncio
    async def test_connect_success(self, store):
        """Conexión exitosa debe establecer _connected."""
        with patch("redis.asyncio.Redis") as mock_redis_cls:
            mock_redis = AsyncMock()
            mock_redis_cls.return_value = mock_redis

            await store.connect()

            assert store._connected is True
            mock_redis.ping.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_failure(self, store):
        """Fallo de conexión debe lanzar excepción."""
        with patch("redis.asyncio.Redis") as mock_redis_cls:
            mock_redis = AsyncMock()
            mock_redis.ping.side_effect = Exception("Redis down")
            mock_redis_cls.return_value = mock_redis

            with pytest.raises(Exception):
                await store.connect()

            assert store._connected is False

    @pytest.mark.asyncio
    async def test_disconnect(self, store):
        """Disconnect debe cerrar cliente."""
        store._client = AsyncMock()
        store._connected = True

        await store.disconnect()

        assert store._connected is False
        store._client.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_incident_success(self, store):
        """add_incident debe almacenar embedding y metadata."""
        store._client = MagicMock()
        pipe = MagicMock()
        pipe.execute = AsyncMock(return_value=None)
        store._client.pipeline = MagicMock(return_value=pipe)

        incident_id = uuid4()
        embedding = [0.1, 0.2, 0.3]
        metadata = {"title": "Test", "category": "network"}

        result = await store.add_incident(incident_id, embedding, metadata)

        assert result is True
        pipe.hset.assert_any_call(INDEX_KEY, str(incident_id), json.dumps(embedding))
        pipe.hset.assert_any_call(DATA_KEY, str(incident_id), json.dumps(metadata))
        pipe.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_incident_no_client(self, store):
        """add_incident sin cliente debe retornar False."""
        store._client = None
        result = await store.add_incident(uuid4(), [0.1], {})
        assert result is False

    @pytest.mark.asyncio
    async def test_add_incident_error(self, store):
        """add_incident con error debe retornar False."""
        store._client = MagicMock()
        store._client.pipeline.side_effect = Exception("Redis error")

        result = await store.add_incident(uuid4(), [0.1], {})
        assert result is False

    @pytest.mark.asyncio
    async def test_search_similar_success(self, store):
        """search_similar debe encontrar similares y ordenar por score."""
        store._client = AsyncMock()

        inc1_id = str(uuid4())
        inc2_id = str(uuid4())

        emb1 = [1.0, 0.0, 0.0]
        emb2 = [0.9, 0.1, 0.0]
        query = [1.0, 0.0, 0.0]

        store._client.hgetall = AsyncMock(return_value={
            inc1_id: json.dumps(emb1),
            inc2_id: json.dumps(emb2),
        })
        store._client.hgetall = AsyncMock(return_value={
            inc1_id: json.dumps(emb1),
            inc2_id: json.dumps(emb2),
        })

        store._client.hgetall.side_effect = None
        store._client.hgetall = AsyncMock()
        store._client.hgetall.return_value = {
            inc1_id: json.dumps(emb1),
            inc2_id: json.dumps(emb2),
        }

        store._client.hgetall.return_value = {
            inc1_id: json.dumps(emb1),
            inc2_id: json.dumps(emb2),
        }

        store._client.hgetall.return_value = {
            inc1_id: json.dumps(emb1),
            inc2_id: json.dumps(emb2),
        }

        all_embeddings = {
            inc1_id: json.dumps(emb1),
            inc2_id: json.dumps(emb2),
        }
        all_data = {
            inc1_id: json.dumps({"title": "Inc1", "category": "network"}),
            inc2_id: json.dumps({"title": "Inc2", "category": "network"}),
        }

        store._client.hgetall = AsyncMock(side_effect=[all_embeddings, all_data])

        results = await store.search_similar(query, limit=5, min_score=0.0)

        assert len(results) >= 2
        assert results[0]["score"] >= results[1]["score"]

    @pytest.mark.asyncio
    async def test_search_similar_with_exclude(self, store):
        """search_similar debe excluir incidente por ID."""
        store._client = AsyncMock()

        inc1_id = str(uuid4())
        inc2_id = str(uuid4())
        exclude = UUID(inc2_id) if isinstance(uuid4(), UUID) else None

        emb = [1.0, 0.0, 0.0]
        store._client.hgetall = AsyncMock(side_effect=[
            {inc1_id: json.dumps(emb), inc2_id: json.dumps(emb)},
            {inc1_id: json.dumps({"title": "Inc1"}), inc2_id: json.dumps({"title": "Inc2"})},
        ])

        results = await store.search_similar(
            [1.0, 0.0, 0.0],
            exclude_id=UUID(inc2_id),
            limit=10,
            min_score=0.0,
        )

        result_ids = [r.get("incident_id") for r in results]
        assert inc2_id not in result_ids

    @pytest.mark.asyncio
    async def test_search_similar_no_client(self, store):
        """search_similar sin cliente debe retornar []."""
        store._client = None
        results = await store.search_similar([0.1])
        assert results == []

    @pytest.mark.asyncio
    async def test_search_similar_min_score(self, store):
        """search_similar debe filtrar por min_score."""
        store._client = AsyncMock()

        inc_id = str(uuid4())
        store._client.hgetall = AsyncMock(side_effect=[
            {inc_id: json.dumps([1.0, 0.0, 0.0])},
            {inc_id: json.dumps({"title": "Test"})},
        ])

        results = await store.search_similar(
            [-1.0, 0.0, 0.0],
            limit=5,
            min_score=0.5,
        )

        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_search_similar_empty_store(self, store):
        """search_similar en store vacío debe retornar []."""
        store._client = AsyncMock()
        store._client.hgetall = AsyncMock(side_effect=[{}, {}])

        results = await store.search_similar([1.0, 0.0, 0.0])
        assert results == []

    @pytest.mark.asyncio
    async def test_delete_incident_success(self, store):
        """delete_incident debe eliminar de ambos índices."""
        store._client = MagicMock()
        pipe = MagicMock()
        pipe.execute = AsyncMock(return_value=None)
        store._client.pipeline = MagicMock(return_value=pipe)

        incident_id = uuid4()
        result = await store.delete_incident(incident_id)

        assert result is True
        pipe.hdel.assert_any_call(INDEX_KEY, str(incident_id))
        pipe.hdel.assert_any_call(DATA_KEY, str(incident_id))
        pipe.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_incident_no_client(self, store):
        """delete_incident sin cliente debe retornar False."""
        store._client = None
        result = await store.delete_incident(uuid4())
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_incident_error(self, store):
        """delete_incident con error debe retornar False."""
        store._client = MagicMock()
        store._client.pipeline.side_effect = Exception("Error")

        result = await store.delete_incident(uuid4())
        assert result is False

    @pytest.mark.asyncio
    async def test_update_incident_embedding(self, store):
        """update_incident debe actualizar embedding."""
        store._client = AsyncMock()

        incident_id = uuid4()
        new_embedding = [0.5, 0.5, 0.5]

        result = await store.update_incident(incident_id, embedding=new_embedding)

        assert result is True
        store._client.hset.assert_called_once_with(
            INDEX_KEY, str(incident_id), json.dumps(new_embedding),
        )

    @pytest.mark.asyncio
    async def test_update_incident_metadata(self, store):
        """update_incident debe mergear metadata existente con nueva."""
        store._client = AsyncMock()

        incident_id = uuid4()
        store._client.hget = AsyncMock(return_value=json.dumps({"title": "Old", "category": "net"}))

        result = await store.update_incident(incident_id, metadata={"priority": 4})

        assert result is True
        args_list = [args for args in store._client.hset.call_args_list]
        last_call = args_list[-1]
        stored = json.loads(last_call[0][2])
        assert stored["title"] == "Old"
        assert stored["priority"] == 4

    @pytest.mark.asyncio
    async def test_update_incident_new_metadata(self, store):
        """update_incident sin metadata existente debe crearla."""
        store._client = AsyncMock()
        store._client.hget = AsyncMock(return_value=None)

        incident_id = uuid4()
        result = await store.update_incident(incident_id, metadata={"title": "New"})

        assert result is True

    @pytest.mark.asyncio
    async def test_update_incident_no_client(self, store):
        """update_incident sin cliente debe retornar False."""
        store._client = None
        result = await store.update_incident(uuid4(), embedding=[0.1])
        assert result is False

    @pytest.mark.asyncio
    async def test_get_incident_found(self, store):
        """get_incident debe retornar metadata del incidente."""
        store._client = AsyncMock()
        store._client.hget = AsyncMock(return_value=json.dumps({"title": "Test"}))

        result = await store.get_incident(uuid4())

        assert result is not None
        assert result["title"] == "Test"

    @pytest.mark.asyncio
    async def test_get_incident_not_found(self, store):
        """get_incident debe retornar None si no existe."""
        store._client = AsyncMock()
        store._client.hget = AsyncMock(return_value=None)

        result = await store.get_incident(uuid4())
        assert result is None

    @pytest.mark.asyncio
    async def test_get_incident_no_client(self, store):
        """get_incident sin cliente debe retornar None."""
        store._client = None
        result = await store.get_incident(uuid4())
        assert result is None

    @pytest.mark.asyncio
    async def test_count(self, store):
        """count debe retornar número de incidentes."""
        store._client = AsyncMock()
        store._client.hlen = AsyncMock(return_value=5)

        count = await store.count()
        assert count == 5

    @pytest.mark.asyncio
    async def test_count_no_client(self, store):
        """count sin cliente debe retornar 0."""
        store._client = None
        count = await store.count()
        assert count == 0

    @pytest.mark.asyncio
    async def test_clear_success(self, store):
        """clear debe eliminar ambas keys."""
        store._client = AsyncMock()

        result = await store.clear()
        assert result is True
        store._client.delete.assert_called_once_with(INDEX_KEY, DATA_KEY)

    @pytest.mark.asyncio
    async def test_clear_no_client(self, store):
        """clear sin cliente debe retornar False."""
        store._client = None
        result = await store.clear()
        assert result is False

    def test_cosine_similarity_same(self, store):
        """Vectores iguales deben tener similitud 1.0."""
        a = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        b = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        assert store._cosine_similarity(a, b) == pytest.approx(1.0)

    def test_cosine_similarity_opposite(self, store):
        """Vectores opuestos deben tener similitud -1.0."""
        a = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        b = np.array([-1.0, 0.0, 0.0], dtype=np.float32)
        assert store._cosine_similarity(a, b) == pytest.approx(-1.0)

    def test_cosine_similarity_orthogonal(self, store):
        """Vectores ortogonales deben tener similitud 0.0."""
        a = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        b = np.array([0.0, 1.0, 0.0], dtype=np.float32)
        assert store._cosine_similarity(a, b) == pytest.approx(0.0)

    def test_cosine_similarity_zero_vector(self, store):
        """Vector cero debe retornar 0.0."""
        a = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        b = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        assert store._cosine_similarity(a, b) == 0.0
