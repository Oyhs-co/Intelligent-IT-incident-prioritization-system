"""
Tests unitarios para el sistema de priorización.

Cubre:
- Carga y limpieza de datos
- Vectorización
- Entrenamiento del modelo
- Predicción y explicabilidad
"""

import unittest
import sys
from pathlib import Path
import tempfile
import shutil
import numpy as np

# Add parent directory to path to import src as package
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_processor import DataProcessor
from src.model_trainer import ModelTrainer
from src.predictor import PriorityPredictor, save_vectorizer
from src.utils import Config, logger, validate_priority


class TestDataProcessor(unittest.TestCase):
    """Tests para DataProcessor."""
    
    def setUp(self):
        self.processor = DataProcessor()
        self.data_file = Config.get_data_path("ITSM_data.csv")
    
    def test_load_data(self):
        """Test: Cargar datos correctamente."""
        if self.data_file.exists():
            df = self.processor.load_data(self.data_file)
            self.assertIsNotNone(df)
            self.assertGreater(len(df), 0)
            self.assertIn("Priority", df.columns)
    
    def test_clean_data(self):
        """Test: Limpieza de datos."""
        if self.data_file.exists():
            df = self.processor.load_data(self.data_file)
            df_clean = self.processor.clean_data(df)
            
            # Verificar que Priority no tiene NaN
            self.assertEqual(df_clean["Priority"].isnull().sum(), 0)
            
            # Verificar que todas las prioridades son válidas
            for priority in df_clean["Priority"]:
                self.assertIn(priority, [1, 2, 3, 4])
    
    def test_generate_incident_text(self):
        """Test: Generación de texto de incidente."""
        if self.data_file.exists():
            df = self.processor.load_data(self.data_file)
            df_clean = self.processor.clean_data(df)
            
            row = df_clean.iloc[0]
            text = self.processor.generate_incident_text(row)
            
            self.assertIsNotNone(text)
            self.assertIsInstance(text, str)
            self.assertGreater(len(text), 0)
    
    def test_vectorize_texts(self):
        """Test: Vectorización TF-IDF."""
        texts = [
            "Hardware failure critical impact",
            "Software bug low impact",
            "Network issue high impact"
        ]
        
        vectors = self.processor.vectorize_texts(texts, fit=True)
        
        self.assertEqual(vectors.shape[0], len(texts))
        self.assertGreater(vectors.shape[1], 0)
    
    def test_validate_priority(self):
        """Test: Validación de prioridad."""
        self.assertTrue(validate_priority(1))
        self.assertTrue(validate_priority(2))
        self.assertTrue(validate_priority(3))
        self.assertTrue(validate_priority(4))
        self.assertFalse(validate_priority(5))
        self.assertFalse(validate_priority(0))
        self.assertFalse(validate_priority("invalid"))


class TestModelTrainer(unittest.TestCase):
    """Tests para ModelTrainer."""
    
    def setUp(self):
        self.trainer = ModelTrainer()
        
        # Datos de prueba
        np.random.seed(Config.RANDOM_STATE)
        self.X_test = np.random.rand(100, 50)
        self.y_test = np.random.randint(1, 5, 100)
    
    def test_create_model(self):
        """Test: Creación del modelo."""
        model = self.trainer.create_model()
        self.assertIsNotNone(model)
    
    def test_train_model(self):
        """Test: Entrenamiento del modelo."""
        self.trainer.create_model()
        self.trainer.train(self.X_test, self.y_test)
        
        self.assertIsNotNone(self.trainer.model)
    
    def test_predict(self):
        """Test: Predicción."""
        self.trainer.create_model()
        self.trainer.train(self.X_test, self.y_test)
        
        predictions = self.trainer.predict(self.X_test[:10])
        
        self.assertEqual(len(predictions), 10)
        for pred in predictions:
            self.assertIn(pred, [1, 2, 3, 4])
    
    def test_predict_proba(self):
        """Test: Predicción con probabilidades."""
        self.trainer.create_model()
        self.trainer.train(self.X_test, self.y_test)
        
        proba = self.trainer.predict_proba(self.X_test[:10])
        
        self.assertEqual(proba.shape[0], 10)
        self.assertEqual(proba.shape[1], 4)
        
        # Verificar que las probabilidades suman 1
        for prob_row in proba:
            self.assertAlmostEqual(prob_row.sum(), 1.0, places=5)


class TestPredictor(unittest.TestCase):
    """Tests para PriorityPredictor."""
    
    def setUp(self):
        # Crear modelo temporal para tests
        Config.ensure_dirs()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Limpia archivos temporales."""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_priority_labels(self):
        """Test: Etiquetas de prioridad."""
        labels = PriorityPredictor.PRIORITY_LABELS
        
        self.assertEqual(len(labels), 4)
        self.assertIn(1, labels)
        self.assertIn(4, labels)


class TestIntegration(unittest.TestCase):
    """Tests de integración completa."""
    
    def setUp(self):
        Config.ensure_dirs()
        self.data_file = Config.get_data_path("ITSM_data.csv")
    
    def test_full_pipeline(self):
        """Test: Pipeline completo (si hay dataset disponible)."""
        if not self.data_file.exists():
            self.skipTest("Dataset ITSM_data.csv no disponible")
        
        # Preprocesamiento
        processor = DataProcessor()
        X_train, X_val, X_test, y_train, y_val, y_test = processor.preprocess_pipeline(
            self.data_file
        )
        
        self.assertGreater(X_train.shape[0], 0)
        self.assertGreater(X_val.shape[0], 0)
        self.assertGreater(X_test.shape[0], 0)
        
        # Entrenamiento
        trainer = ModelTrainer()
        trainer.create_model()
        trainer.train(X_train, y_train)
        
        # Validación y test
        val_metrics = trainer.validate(X_val, y_val)
        test_metrics = trainer.test(X_test, y_test)
        
        # Verificaciones
        self.assertIn("accuracy", val_metrics)
        self.assertIn("accuracy", test_metrics)
        
        # Verificar que accuracy está en rango válido
        self.assertGreaterEqual(test_metrics["accuracy"], 0)
        self.assertLessEqual(test_metrics["accuracy"], 1)
        
        logger.info(f"✓ Test accuracy alcanzado: {test_metrics['accuracy']:.4f}")


def run_tests():
    """Ejecuta todos los tests."""
    
    # Crear suite de tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Agregar tests
    suite.addTests(loader.loadTestsFromTestCase(TestDataProcessor))
    suite.addTests(loader.loadTestsFromTestCase(TestModelTrainer))
    suite.addTests(loader.loadTestsFromTestCase(TestPredictor))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Ejecutar
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
