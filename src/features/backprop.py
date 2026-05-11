from dataclasses import dataclass
import numpy as np


@dataclass
class LogisticNeuron:
    w: np.ndarray
    b: float = 0.0

    @staticmethod
    def sigmoid(z: np.ndarray) -> np.ndarray:
        return 1.0 / (1.0 + np.exp(-z))

    def forward(self, x: np.ndarray) -> np.ndarray:
        return self.sigmoid(x @ self.w + self.b)

    def loss_and_grad(self, x: np.ndarray, y: np.ndarray) -> tuple[float, np.ndarray, float]:
        o = self.forward(x)
        eps = 1e-8
        loss = float(-np.mean(y * np.log(o + eps) + (1.0 - y) * np.log(1.0 - o + eps)))

        dz = (o - y) / max(1, x.shape[0])
        dw = x.T @ dz
        db = float(np.sum(dz))
        return loss, dw.astype(np.float32), db