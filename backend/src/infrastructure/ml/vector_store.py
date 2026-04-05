"""Vector store para búsqueda de similitud."""

from __future__ import annotations

from typing import Any, Optional
from uuid import UUID
import json
import numpy as np

import redis.asyncio as redis

from src.shared.logging import get_logger

logger = get_logger("ml.vector_store")

INDEX_KEY = "incident_embeddings:index"
DATA_KEY = "incident_embeddings:data"


class IncidentVectorStore:
    """Vector store para incidentes usando Redis."""

    def __init__(
        self,
        embedding_dim: int = 384,
        host: str = "localhost",
        port: int = 6379,
        db: int = 1,
        password: Optional[str] = None,
    ):
        self._embedding_dim = embedding_dim
        self._host = host
        self._port = port
        self._db = db
        self._password = password
        self._client: Optional[redis.Redis] = None
        self._connected = False

    async def connect(self) -> None:
        """Establece conexión con Redis."""
        try:
            self._client = redis.Redis(
                host=self._host,
                port=self._port,
                db=self._db,
                password=self._password,
                decode_responses=True,
            )
            await self._client.ping()
            self._connected = True
            logger.info("Connected to Vector Store Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Vector Store: {e}")
            self._connected = False
            raise

    async def disconnect(self) -> None:
        """Cierra la conexión."""
        if self._client:
            await self._client.close()
        self._connected = False

    async def add_incident(
        self,
        incident_id: UUID,
        embedding: list[float],
        metadata: dict[str, Any],
    ) -> bool:
        """Añade un incidente al vector store."""
        if not self._client:
            return False

        try:
            key = str(incident_id)
            embedding_json = json.dumps(embedding)
            metadata["incident_id"] = key

            pipe = self._client.pipeline()
            pipe.hset(INDEX_KEY, key, embedding_json)
            pipe.hset(DATA_KEY, key, json.dumps(metadata))
            await pipe.execute()

            logger.info("Incident added to vector store", incident_id=key)
            return True

        except Exception as e:
            logger.error(f"Failed to add incident to vector store: {e}")
            return False

    async def search_similar(
        self,
        embedding: list[float],
        exclude_id: Optional[UUID] = None,
        limit: int = 5,
        min_score: float = 0.0,
    ) -> list[dict[str, Any]]:
        """Busca incidentes similares."""
        if not self._client:
            return []

        try:
            exclude_key = str(exclude_id) if exclude_id else None
            query_vector = np.array(embedding, dtype=np.float32)

            all_embeddings = await self._client.hgetall(INDEX_KEY)
            all_metadata = await self._client.hgetall(DATA_KEY)

            results = []
            for key, emb_str in all_embeddings.items():
                if exclude_key and key == exclude_key:
                    continue

                stored_vector = np.array(json.loads(emb_str), dtype=np.float32)
                similarity = self._cosine_similarity(query_vector, stored_vector)

                if similarity >= min_score:
                    metadata = json.loads(all_metadata.get(key, "{}"))
                    metadata["score"] = float(similarity)
                    results.append(metadata)

            results.sort(key=lambda x: x["score"], reverse=True)
            return results[:limit]

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    async def delete_incident(self, incident_id: UUID) -> bool:
        """Elimina un incidente del vector store."""
        if not self._client:
            return False

        try:
            key = str(incident_id)
            pipe = self._client.pipeline()
            pipe.hdel(INDEX_KEY, key)
            pipe.hdel(DATA_KEY, key)
            await pipe.execute()
            logger.info("Incident deleted from vector store", incident_id=key)
            return True
        except Exception as e:
            logger.error(f"Failed to delete incident: {e}")
            return False

    async def update_incident(
        self,
        incident_id: UUID,
        embedding: Optional[list[float]] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> bool:
        """Actualiza un incidente en el vector store."""
        if not self._client:
            return False

        try:
            key = str(incident_id)

            if embedding:
                await self._client.hset(INDEX_KEY, key, json.dumps(embedding))

            if metadata:
                existing = await self._client.hget(DATA_KEY, key)
                if existing:
                    existing_data = json.loads(existing)
                    existing_data.update(metadata)
                    metadata = existing_data
                else:
                    metadata["incident_id"] = key
                await self._client.hset(DATA_KEY, key, json.dumps(metadata))

            return True

        except Exception as e:
            logger.error(f"Failed to update incident: {e}")
            return False

    async def get_incident(self, incident_id: UUID) -> Optional[dict[str, Any]]:
        """Obtiene un incidente del vector store."""
        if not self._client:
            return None

        try:
            key = str(incident_id)
            metadata = await self._client.hget(DATA_KEY, key)
            if metadata:
                return json.loads(metadata)
            return None
        except Exception as e:
            logger.error(f"Failed to get incident: {e}")
            return None

    async def count(self) -> int:
        """Cuenta el número de incidentes en el store."""
        if not self._client:
            return 0
        return await self._client.hlen(INDEX_KEY)

    async def clear(self) -> bool:
        """Limpia todo el vector store."""
        if not self._client:
            return False

        try:
            await self._client.delete(INDEX_KEY, DATA_KEY)
            logger.info("Vector store cleared")
            return True
        except Exception as e:
            logger.error(f"Failed to clear vector store: {e}")
            return False

    @staticmethod
    def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        """Calcula similitud coseno."""
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))
