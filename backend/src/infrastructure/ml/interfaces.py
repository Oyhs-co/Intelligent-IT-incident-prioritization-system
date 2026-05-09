from abc import ABC, abstractmethod
from pathlib import Path

import numpy as np


class IEncoder(ABC):
    @abstractmethod
    def encode(self, texts: list[str], batch_size: int = 32) -> np.ndarray:
        pass

    @abstractmethod
    def get_dimension(self) -> int:
        pass

    @abstractmethod
    def save(self, path: Path) -> None:
        pass

    @classmethod
    @abstractmethod
    def load(cls, path: Path) -> 'IEncoder':
        pass


class IClassifier(ABC):
    @abstractmethod
    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        pass

    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        pass

    @abstractmethod
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        pass

    @abstractmethod
    def save(self, path: Path) -> None:
        pass

    @abstractmethod
    def load(self, path: Path) -> None:
        pass

    @abstractmethod
    def get_feature_importance(self, X: np.ndarray, y: np.ndarray) -> np.ndarray | None:
        pass
