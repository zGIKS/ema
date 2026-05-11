import numpy as np


class GradientDescent:
    lr: float = 0.05

    def step(self, params: np.ndarray, grad: np.ndarray) -> np.ndarray:
        return params - self.lr * grad


class StochasticGradientDescent:
    lr: float = 0.05

    def step(self, params: np.ndarray, grad: np.ndarray) -> np.ndarray:
        return params - self.lr * grad


class Momentum:
    lr: float = 0.05
    gamma: float = 0.9

    def __post_init__(self) -> None:
        self._v: np.ndarray | None = None

    def step(self, params: np.ndarray, grad: np.ndarray) -> np.ndarray:
        if self._v is None:
            self._v = np.zeros_like(params, dtype=np.float32)
        self._v = self.gamma * self._v + self.lr * grad
        return params - self._v


class Adam:
    lr: float = 0.05
    beta1: float = 0.9
    beta2: float = 0.999
    eps: float = 1e-8

    def __post_init__(self) -> None:
        self._m: np.ndarray | None = None
        self._v: np.ndarray | None = None
        self._t: int = 0

    def step(self, params: np.ndarray, grad: np.ndarray) -> np.ndarray:
        if self._m is None:
            self._m = np.zeros_like(params, dtype=np.float32)
            self._v = np.zeros_like(params, dtype=np.float32)
        self._t += 1

        self._m = self.beta1 * self._m + (1.0 - self.beta1) * grad
        self._v = self.beta2 * self._v + (1.0 - self.beta2) * (grad * grad)

        m_hat = self._m / (1.0 - (self.beta1**self._t))
        v_hat = self._v / (1.0 - (self.beta2**self._t))
        return params - self.lr * m_hat / (np.sqrt(v_hat) + self.eps)