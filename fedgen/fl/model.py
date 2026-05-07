"""
Logistic Regression model implemented in pure NumPy.
Supports weight export/import for federated averaging.
"""
import numpy as np


class LogisticRegression:
    """Binary logistic regression with SGD, designed for federated learning."""

    def __init__(self, n_features: int, lr: float = 0.1, seed: int = 42):
        rng = np.random.RandomState(seed)
        self.weights = rng.randn(n_features) * 0.01
        self.bias = 0.0
        self.lr = lr

    def _sigmoid(self, z: np.ndarray) -> np.ndarray:
        z = np.clip(z, -500, 500)
        return 1.0 / (1.0 + np.exp(-z))

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self._sigmoid(X @ self.weights + self.bias)

    def predict(self, X: np.ndarray) -> np.ndarray:
        return (self.predict_proba(X) >= 0.5).astype(int)

    def train_epoch(self, X: np.ndarray, y: np.ndarray) -> float:
        """One epoch of mini-batch SGD. Returns average loss."""
        n = len(y)
        indices = np.random.permutation(n)
        batch_size = min(32, n)
        total_loss = 0.0
        n_batches = 0

        for start in range(0, n, batch_size):
            idx = indices[start:start + batch_size]
            X_b, y_b = X[idx], y[idx]
            probs = self.predict_proba(X_b)

            # Binary cross-entropy gradient
            error = probs - y_b
            grad_w = (X_b.T @ error) / len(y_b)
            grad_b = np.mean(error)

            self.weights -= self.lr * grad_w
            self.bias -= self.lr * grad_b

            # Loss
            eps = 1e-15
            probs_clipped = np.clip(probs, eps, 1 - eps)
            loss = -np.mean(y_b * np.log(probs_clipped) + (1 - y_b) * np.log(1 - probs_clipped))
            total_loss += loss
            n_batches += 1

        return total_loss / max(n_batches, 1)

    def get_weights(self) -> dict:
        """Export model weights for federated aggregation."""
        return {"weights": self.weights.copy(), "bias": float(self.bias)}

    def set_weights(self, params: dict):
        """Import model weights from federated aggregation."""
        self.weights = params["weights"].copy()
        self.bias = params["bias"]

    def accuracy(self, X: np.ndarray, y: np.ndarray) -> float:
        preds = self.predict(X)
        return float(np.mean(preds == y))
