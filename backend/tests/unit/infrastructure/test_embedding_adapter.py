"""Tests unitarios para MiniLMEmbeddingAdapter y TFIDFEmbeddingAdapter."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from src.infrastructure.ml.embedding_adapter import (
    MiniLMEmbeddingAdapter,
    TFIDFEmbeddingAdapter,
)


class TestMiniLMEmbeddingAdapter:
    """Tests para MiniLMEmbeddingAdapter."""

    @pytest.fixture
    def adapter(self):
        with patch("src.infrastructure.ml.embedding_adapter.MiniLMEncoder") as mock:
            mock.return_value = MagicMock()
            mock.return_value.get_dimension.return_value = 384
            mock.return_value.encode.return_value = np.array(
                [[0.1, 0.2, 0.3]], dtype=np.float32
            )
            yield MiniLMEmbeddingAdapter(model_name="all-MiniLM-L6-v2")

    def test_is_available(self, adapter):
        assert adapter.is_available() is True

    def test_get_dimension(self, adapter):
        assert adapter.get_dimension() == 384

    async def test_generate_embedding(self, adapter):
        result = await adapter.generate_embedding("test text")
        assert isinstance(result, list)
        assert len(result) == 3
        assert result[0] == pytest.approx(0.1, rel=1e-5)

    async def test_generate_embedding_delegates_to_encoder(self, adapter):
        adapter._encoder.encode.reset_mock()
        await adapter.generate_embedding("hello")
        adapter._encoder.encode.assert_called_once_with(["hello"])

    async def test_generate_batch(self, adapter):
        adapter._encoder.encode.return_value = np.array(
            [[0.1, 0.2], [0.3, 0.4]], dtype=np.float32
        )
        results = await adapter.generate_batch(["text1", "text2"])
        assert len(results) == 2
        assert len(results[0]) == 2

    async def test_generate_batch_delegates_to_encoder(self, adapter):
        adapter._encoder.encode.reset_mock()
        await adapter.generate_batch(["a", "b"])
        adapter._encoder.encode.assert_called_once_with(["a", "b"])


class TestTFIDFEmbeddingAdapter:
    """Tests para TFIDFEmbeddingAdapter."""

    @pytest.fixture
    def adapter(self):
        with patch("src.infrastructure.ml.embedding_adapter.TFIDFEncoder") as mock:
            mock.return_value = MagicMock()
            mock.return_value.get_dimension.return_value = 100
            mock.return_value.encode.return_value = np.array(
                [[0.5, 0.5]], dtype=np.float32
            )
            yield TFIDFEmbeddingAdapter(max_features=100)

    def test_is_available(self, adapter):
        assert adapter.is_available() is True

    def test_get_dimension(self, adapter):
        assert adapter.get_dimension() == 100

    async def test_generate_embedding(self, adapter):
        result = await adapter.generate_embedding("hello world")
        assert isinstance(result, list)
        assert len(result) == 2

    async def test_generate_embedding_delegates_to_encoder(self, adapter):
        adapter._encoder.encode.reset_mock()
        await adapter.generate_embedding("hello world")
        adapter._encoder.encode.assert_called_once_with(["hello world"])

    async def test_generate_batch(self, adapter):
        adapter._encoder.encode.return_value = np.array(
            [[0.5, 0.5], [0.3, 0.7]], dtype=np.float32
        )
        results = await adapter.generate_batch(["text1", "text2"])
        assert len(results) == 2
        assert len(results[0]) == 2

    async def test_generate_batch_delegates_to_encoder(self, adapter):
        adapter._encoder.encode.reset_mock()
        await adapter.generate_batch(["a", "b"])
        adapter._encoder.encode.assert_called_once_with(["a", "b"])

    async def test_generate_batch_empty(self, adapter):
        adapter._encoder.encode.return_value = np.array([[]], dtype=np.float32).reshape(0, 0)
        result = await adapter.generate_batch([])
        assert len(result) == 0
