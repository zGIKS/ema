from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class GradientDescent:
    """
    ## 1. Gradient Descent

    Minimiza una función de costo J(theta) actualizando:

      theta_{t+1} = theta_t - eta * ∇J(theta_t)

    Usamos esto en calibración (ajustar umbral/margen) donde theta son pocos parámetros
    y el gradiente es barato de calcular.
    """

    lr: float = 0.05

    def step(self, params: np.ndarray, grad: np.ndarray) -> np.ndarray:
        return params - self.lr * grad


@dataclass
class StochasticGradientDescent:
    """
    ## 2. Stochastic Gradient Descent (SGD)

    Igual a GD pero el gradiente se estima con una muestra/batch pequeño:

      theta = theta - eta * ∇J(theta; x^(i), y^(i))

    En este repo lo usamos para calibrar con pares (positivos/negativos) de embeddings
    muestreados aleatoriamente.
    """

    lr: float = 0.05

    def step(self, params: np.ndarray, grad: np.ndarray) -> np.ndarray:
        return params - self.lr * grad


@dataclass
class Momentum:
    """
    ## 3. Momentum

    Introduce "inercia" acumulando un vector de velocidad:

      v_t = gamma * v_{t-1} + eta * ∇J(theta_t)
      theta_{t+1} = theta_t - v_t

    En calibración ayuda a estabilizar la búsqueda del umbral cuando hay ruido (SGD).
    """

    lr: float = 0.05
    gamma: float = 0.9

    def __post_init__(self) -> None:
        self._v: np.ndarray | None = None

    def step(self, params: np.ndarray, grad: np.ndarray) -> np.ndarray:
        if self._v is None:
            self._v = np.zeros_like(params, dtype=np.float32)
        self._v = self.gamma * self._v + self.lr * grad
        return params - self._v


@dataclass
class Adam:
    """
    ## 4. Adam Optimizer

    Combina momentum (1er momento) + learning rate adaptativo (2do momento):

      m_t = beta1*m_{t-1} + (1-beta1)*g_t
      v_t = beta2*v_{t-1} + (1-beta2)*g_t^2
      m̂_t = m_t / (1 - beta1^t)
      v̂_t = v_t / (1 - beta2^t)
      theta_t = theta_{t-1} - lr * m̂_t / (sqrt(v̂_t) + eps)

    En calibración suele converger más rápido y con menos tuning.
    """

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

