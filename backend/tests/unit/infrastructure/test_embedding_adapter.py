"""Tests unitarios para SentenceTransformerEmbedding y TFIDFEmbedding."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from src.infrastructure.ml.embedding_adapter import (
    SentenceTransformerEmbedding,
    TFIDFEmbedding,
)


class TestSentenceTransformerEmbedding:
    """Tests para SentenceTransformerEmbedding."""

    @pytest.fixture
    def embedding(self):
        return SentenceTransformerEmbedding(model_name="all-MiniLM-L6-v2")

    def test_init(self, embedding):
        """Inicialización debe establecer valores por defecto."""
        assert embedding._model_name == "all-MiniLM-L6-v2"
        assert embedding._model is None

    def test_is_available_no_model(self, embedding):
        """Sin modelo cargado is_available debe retornar False."""
        with patch.object(embedding, "_load_model") as mock_load:
            mock_load.return_value = None
            embedding._model = None
            assert embedding.is_available() is False

    def test_is_available_with_model(self, embedding):
        """Con modelo cargado is_available debe retornar True."""
        embedding._model = MagicMock()
        assert embedding.is_available() is True

    def test_get_dimension_default(self, embedding):
        """get_dimension sin modelo debe retornar 384."""
        with patch.object(embedding, "_load_model"):
            embedding._dimension = None
            dim = embedding.get_dimension()
            assert dim == 384

    def test_get_dimension_with_model(self, embedding):
        """get_dimension con modelo debe retornar dimensión real."""
        embedding._dimension = 768
        embedding._model = MagicMock()
        dim = embedding.get_dimension()
        assert dim == 768

    async def test_generate_embedding_fallback(self, embedding):
        """Sin modelo debe generar embedding fallback."""
        with patch.object(embedding, "_load_model"):
            embedding._model = None
            result = await embedding.generate_embedding("test text")

            assert isinstance(result, list)
            assert len(result) == 384
            assert all(isinstance(v, float) for v in result)

    async def test_generate_embedding_fallback_normalized(self, embedding):
        """Fallback embedding debe estar normalizado."""
        with patch.object(embedding, "_load_model"):
            embedding._model = None
            result = await embedding.generate_embedding("some long text here with multiple words")

            vec = np.array(result, dtype=np.float32)
            norm = np.linalg.norm(vec)
            assert norm == pytest.approx(1.0, rel=0.01)

    async def test_generate_embedding_with_model(self, embedding):
        """Con modelo debe generar embedding real."""
        mock_model = MagicMock()
        mock_model.encode.return_value = np.array([0.1, 0.2, 0.3], dtype=np.float32)
        embedding._model = mock_model
        embedding._dimension = 3

        result = await embedding.generate_embedding("test")

        assert isinstance(result, list)
        assert len(result) == 3
        assert result[0] == pytest.approx(0.1, rel=1e-5)
        assert result[1] == pytest.approx(0.2, rel=1e-5)
        assert result[2] == pytest.approx(0.3, rel=1e-5)

    async def test_generate_embedding_model_error(self, embedding):
        """Error del modelo debe usar fallback."""
        mock_model = MagicMock()
        mock_model.encode.side_effect = Exception("Model error")
        embedding._model = mock_model

        result = await embedding.generate_embedding("test")

        assert isinstance(result, list)
        assert len(result) == 384

    async def test_generate_batch_fallback(self, embedding):
        """Batch sin modelo debe generar fallbacks."""
        with patch.object(embedding, "_load_model"):
            embedding._model = None
            results = await embedding.generate_batch(["text1", "text2"])

            assert len(results) == 2
            assert all(len(r) == 384 for r in results)

    async def test_generate_batch_with_model(self, embedding):
        """Batch con modelo debe generar embeddings."""
        mock_model = MagicMock()
        mock_model.encode.return_value = np.array([[0.1, 0.2], [0.3, 0.4]], dtype=np.float32)
        embedding._model = mock_model

        results = await embedding.generate_batch(["text1", "text2"])

        assert len(results) == 2
        assert len(results[0]) == 2

    async def test_generate_batch_error(self, embedding):
        """Error en batch debe usar fallback."""
        mock_model = MagicMock()
        mock_model.encode.side_effect = Exception("Error")
        embedding._model = mock_model

        results = await embedding.generate_batch(["text1", "text2"])

        assert len(results) == 2
        assert all(len(r) == 384 for r in results)

    def test_fallback_embedding_deterministic(self, embedding):
        """Mismo texto debe generar mismo embedding fallback."""
        e1 = embedding._generate_fallback_embedding("same text")
        e2 = embedding._generate_fallback_embedding("same text")

        assert e1 == e2

    def test_fallback_embedding_different(self, embedding):
        """Textos diferentes deben generar embeddings diferentes."""
        e1 = embedding._generate_fallback_embedding("hello world")
        e2 = embedding._generate_fallback_embedding("goodbye world")

        assert e1 != e2

    def test_fallback_embedding_empty(self, embedding):
        """Texto vacío debe generar embedding válido."""
        result = embedding._generate_fallback_embedding("")
        assert len(result) == 384
        assert all(v == 0.0 for v in result)


class TestTFIDFEmbedding:
    """Tests para TFIDFEmbedding."""

    @pytest.fixture
    def tfidf(self):
        return TFIDFEmbedding(max_features=100)

    def test_init(self, tfidf):
        """Inicialización debe establecer valores."""
        assert tfidf._max_features == 100
        assert tfidf._fitted is False

    def test_is_available(self, tfidf):
        """TFIDF siempre está disponible."""
        assert tfidf.is_available() is True

    def test_get_dimension_not_fitted(self, tfidf):
        """get_dimension sin fit debe retornar max_features."""
        assert tfidf.get_dimension() == 100

    def test_get_dimension_fitted(self, tfidf):
        """get_dimension con fit debe retornar tamaño del vocabulario."""
        tfidf._vocabulary = {"hello": 0, "world": 1}
        assert tfidf.get_dimension() == 2

    def test_tokenize(self, tfidf):
        """_tokenize debe dividir en palabras."""
        assert tfidf._tokenize("hello world") == ["hello", "world"]

    def test_fit(self, tfidf):
        """_fit debe construir vocabulario."""
        tfidf._fit(["hello world", "world peace"])

        assert tfidf._fitted is True
        assert "hello" in tfidf._vocabulary
        assert "world" in tfidf._vocabulary
        assert tfidf._idf is not None

    def test_fit_already_fitted(self, tfidf):
        """_fit no debe re-ajustar si ya está fitted."""
        tfidf._fitted = True
        tfidf._vocabulary = {"only": 0}

        tfidf._fit(["new data"])
        assert len(tfidf._vocabulary) == 1

    async def test_generate_embedding(self, tfidf):
        """generate_embedding debe producir vector TF-IDF."""
        embedding = await tfidf.generate_embedding("hello world hello")

        assert isinstance(embedding, list)
        assert len(embedding) == 2
        assert embedding[0] > 0
        assert embedding[1] > 0

    async def test_generate_embedding_normalized(self, tfidf):
        """Embedding TF-IDF debe estar normalizado."""
        embedding = await tfidf.generate_embedding("hello world hello")

        vec = np.array(embedding, dtype=np.float32)
        norm = np.linalg.norm(vec)
        assert norm == pytest.approx(1.0, rel=0.01)

    async def test_generate_embedding_empty_text(self, tfidf):
        """Texto vacío debe generar vector cero."""
        embedding = await tfidf.generate_embedding("")

        vec = np.array(embedding, dtype=np.float32)
        assert np.linalg.norm(vec) == 0.0

    async def test_generate_batch(self, tfidf):
        """generate_batch debe generar embeddings para múltiples textos."""
        embeddings = await tfidf.generate_batch(["hello world", "goodbye world"])

        assert len(embeddings) == 2
        assert len(embeddings[0]) > 0
        assert len(embeddings[1]) > 0

    async def test_generate_batch_calls_fit(self, tfidf):
        """generate_batch debe hacer fit con todos los textos."""
        texts = ["hello world", "world peace", "hello again"]

        with patch.object(tfidf, "_fit") as mock_fit:
            mock_fit.return_value = None
            tfidf._fitted = False
            tfidf._vocabulary = {"hello": 0, "world": 1, "peace": 2, "again": 3}
            tfidf._idf = np.ones(4)

            with patch.object(tfidf, "generate_embedding") as mock_gen:
                mock_gen.return_value = [0.5, 0.5, 0.5, 0.5]
                await tfidf.generate_batch(texts)
                mock_fit.assert_called_once_with(texts)

    async def test_generate_batch_empty(self, tfidf):
        """Lista vacía debe retornar lista vacía."""
        tfidf._fitted = True
        tfidf._vocabulary = {}
        tfidf._idf = np.array([])

        results = await tfidf.generate_batch([])
        assert results == []

    def test_fit_respects_max_features(self, tfidf):
        """fit debe limitar vocabulario a max_features."""
        texts = [f"word{i}" for i in range(200)]
        tfidf._fit(texts)

        assert len(tfidf._vocabulary) <= 100

    def test_get_dimension_after_fit(self, tfidf):
        """get_dimension después de fit debe coincidir con vocabulario."""
        tfidf._fit(["hello world foo bar"])
        assert tfidf.get_dimension() == 4
