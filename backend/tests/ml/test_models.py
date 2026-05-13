"""Tests unitarios para el sistema de priorización (migrados desde IA-module)."""

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.infrastructure.ml._utils import Config, validate_priority
from src.infrastructure.ml.classifiers import (
    FallbackEnsembleClassifier,
    LightGBMClassifier,
)
from src.infrastructure.ml.data_processor import DataProcessor
from src.infrastructure.ml.encoders import TFIDFEncoder
from src.infrastructure.ml.model_trainer import ModelFactory, ModelTrainer
from src.infrastructure.ml.predictor import PriorityPredictor


class TestDataProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = DataProcessor()
        self.data_file = Config.get_data_path("it_tickets_merged.csv")

    def test_load_data(self):
        if self.data_file.exists():
            df = self.processor.load_data(self.data_file)
            self.assertIsNotNone(df)
            self.assertGreater(len(df), 0)
            self.assertIn("priority", df.columns)

    def test_clean_data(self):
        if self.data_file.exists():
            df = self.processor.load_data(self.data_file)
            df_clean = self.processor.clean_data(df)
            self.assertEqual(df_clean["priority"].isnull().sum(), 0)
            for priority in df_clean["priority"]:
                self.assertIn(priority, [1, 2, 3])

    def test_prepare_texts_and_labels(self):
        if self.data_file.exists():
            df = self.processor.load_data(self.data_file)
            df_clean = self.processor.clean_data(df)
            texts, labels = self.processor.prepare_texts_and_labels(df_clean)
            self.assertIsNotNone(texts)
            self.assertIsNotNone(labels)
            self.assertEqual(len(texts), len(labels))
            self.assertEqual(len(texts), len(df_clean))
            for label in labels:
                self.assertIn(label, [0, 1, 2])

    def test_encode_texts_tfidf(self):
        texts = [
            "Hardware failure critical impact server down",
            "Software bug low impact application error",
            "Network issue high impact connectivity problems",
            "Security incident critical data breach",
            "Password reset medium priority user request"
        ]
        encoder = TFIDFEncoder(max_features=100)
        vectors = encoder.encode(texts)
        self.assertEqual(vectors.shape[0], len(texts))
        self.assertGreater(vectors.shape[1], 0)
        self.assertEqual(encoder.get_dimension(), vectors.shape[1])

    def test_encode_texts_save_load(self):
        texts = ["test one", "test two"]
        encoder = TFIDFEncoder(max_features=10)
        encoder.encode(texts)
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            encoder.save(tmppath / "encoder")
            loaded = TFIDFEncoder.load(tmppath / "encoder")
            self.assertEqual(loaded.get_dimension(), encoder.get_dimension())

    def test_validate_priority(self):
        self.assertTrue(validate_priority(1))
        self.assertTrue(validate_priority(2))
        self.assertTrue(validate_priority(3))
        self.assertFalse(validate_priority(4))
        self.assertFalse(validate_priority(0))
        self.assertFalse(validate_priority("invalid"))


class TestEncoders(unittest.TestCase):
    def test_tfidf_basic(self):
        texts = ["hello world", "world test", "hello test data"]
        encoder = TFIDFEncoder(max_features=50)
        X = encoder.encode(texts)
        self.assertEqual(X.shape[0], 3)
        self.assertGreater(X.shape[1], 0)

    def test_tfidf_transform(self):
        train_texts = ["hello world", "test data"]
        test_texts = ["hello test"]
        encoder = TFIDFEncoder(max_features=50)
        encoder.encode(train_texts)
        X_test = encoder.encode(test_texts)
        self.assertEqual(X_test.shape[0], 1)


class TestClassifiers(unittest.TestCase):
    def setUp(self):
        np.random.seed(42)
        self.X = np.random.rand(100, 50).astype(np.float32)
        self.y = np.random.randint(0, 3, 100).astype(np.int32)

    def test_lightgbm_create(self):
        clf = LightGBMClassifier(n_classes=3)
        self.assertIsNotNone(clf)

    def test_lightgbm_train_predict(self):
        clf = LightGBMClassifier(n_classes=3, n_estimators=20)
        clf.fit(self.X, self.y)
        preds = clf.predict(self.X[:10])
        self.assertEqual(len(preds), 10)
        proba = clf.predict_proba(self.X[:10])
        self.assertEqual(proba.shape, (10, 3))

    def test_lightgbm_save_load(self):
        clf = LightGBMClassifier(n_classes=3, n_estimators=20)
        clf.fit(self.X, self.y)
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir) / "model.txt"
            clf.save(tmppath)
            loaded = LightGBMClassifier(n_classes=3)
            loaded.load(tmppath)
            preds1 = clf.predict(self.X[:5])
            preds2 = loaded.predict(self.X[:5])
            np.testing.assert_array_equal(preds1, preds2)

    def test_ensemble(self):
        clf = FallbackEnsembleClassifier(lgb_weight=0.6)
        clf.fit(self.X, self.y)
        preds = clf.predict(self.X[:10])
        self.assertEqual(len(preds), 10)


class TestModelTrainer(unittest.TestCase):
    def setUp(self):
        np.random.seed(42)
        self.X_train = np.random.rand(80, 30).astype(np.float32)
        self.y_train = np.random.randint(0, 3, 80).astype(np.int32)
        self.X_val = np.random.rand(20, 30).astype(np.float32)
        self.y_val = np.random.randint(0, 3, 20).astype(np.int32)

    def test_trainer_create(self):
        trainer = ModelTrainer()
        self.assertIsNotNone(trainer)

    def test_trainer_with_lightgbm(self):
        classifier = ModelFactory.create_lightgbm(n_classes=3)
        trainer = ModelTrainer(classifier=classifier, random_state=42)
        trainer.train(self.X_train, self.y_train)
        metrics = trainer.evaluate(self.X_val, self.y_val, "Test")
        self.assertIn("accuracy", metrics)
        self.assertIn("f1", metrics)
        self.assertGreaterEqual(metrics["accuracy"], 0)
        self.assertLessEqual(metrics["accuracy"], 1)

    def test_trainer_predict_proba(self):
        classifier = ModelFactory.create_lightgbm(n_classes=3)
        trainer = ModelTrainer(classifier=classifier, random_state=42)
        trainer.train(self.X_train, self.y_train)
        proba = trainer.predict_proba(self.X_val[:5])
        self.assertEqual(proba.shape, (5, 3))
        for row in proba:
            self.assertAlmostEqual(row.sum(), 1.0, places=5)


class TestPredictor(unittest.TestCase):
    def setUp(self):
        Config.ensure_dirs()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    def test_priority_labels(self):
        self.assertEqual(len(PriorityPredictor.PRIORITY_LABELS), 3)
        self.assertIn(0, PriorityPredictor.PRIORITY_LABELS)
        self.assertIn(2, PriorityPredictor.PRIORITY_LABELS)

    def test_priority_descriptions(self):
        self.assertEqual(len(PriorityPredictor.PRIORITY_DESCRIPTIONS), 3)


class TestIntegration(unittest.TestCase):
    def setUp(self):
        Config.ensure_dirs()
        self.data_file = Config.get_data_path("it_tickets_merged.csv")

    def test_full_pipeline_tfidf(self):
        if not self.data_file.exists():
            self.skipTest("Dataset it_tickets_merged.csv no disponible")
        processor = DataProcessor()
        result = processor.preprocess_pipeline(
            input_file=self.data_file,
            encoder=None,
            use_embeddings=False
        )
        X_train, X_val, X_test, y_train, y_val, y_test, encoder = result
        from sklearn.linear_model import LogisticRegression
        classifier = LogisticRegression(max_iter=1000, random_state=42)
        trainer = ModelTrainer(classifier=classifier, encoder=encoder)
        trainer.train(X_train, y_train)
        metrics = trainer.test(X_test, y_test)
        self.assertIn("accuracy", metrics)
        self.assertGreaterEqual(metrics["accuracy"], 0)

    def test_predictor_explain(self):
        if not Config.MODEL_FILE.exists():
            self.skipTest("Modelo no entrenado, saltando test")
        predictor = PriorityPredictor()
        text = "Critical system failure urgent"
        explanation = predictor.explain_prediction(text, top_k=3)
        self.assertIn("predicted_priority", explanation)
        self.assertIn("confidence", explanation)
        self.assertIn("priority_label", explanation)
        self.assertIn("contributing_features", explanation)


if __name__ == "__main__":
    unittest.main()
