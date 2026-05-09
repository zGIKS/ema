from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from src.algorithms.optimizers import Adam, GradientDescent, Momentum, StochasticGradientDescent


@dataclass(frozen=True)
class CalibrationResult:
    threshold: float
    min_margin: float
    loss: float


class ThresholdCalibrator:
    """
    Calibra (threshold, min_margin) sobre un set de similitudes con etiquetas.

    Usos reales:
    - Cuando tienes 1 foto por persona, los scores bajan. Calibrar con tus propios datos
      te da el mejor tradeoff entre falsos positivos y falsos negativos.

    Parámetros a aprender:
      theta = [threshold, min_margin]

    Optimización:
    - Se puede entrenar con GD / SGD / Momentum / Adam (algoritmos 1-4).
    """

    def __init__(self, optimizer: str = "adam", lr: float = 0.05):
        self.optimizer_name = optimizer.lower()
        if self.optimizer_name == "gd":
            self.opt = GradientDescent(lr=lr)
        elif self.optimizer_name == "sgd":
            self.opt = StochasticGradientDescent(lr=lr)
        elif self.optimizer_name == "momentum":
            self.opt = Momentum(lr=lr, gamma=0.9)
        elif self.optimizer_name == "adam":
            self.opt = Adam(lr=lr)
        else:
            raise ValueError("optimizer must be one of: gd, sgd, momentum, adam")

    @staticmethod
    def _sigmoid(z: np.ndarray) -> np.ndarray:
        return 1.0 / (1.0 + np.exp(-z))

    def fit(
        self,
        pos_sims: np.ndarray,
        neg_sims: np.ndarray,
        init_threshold: float = 0.80,
        init_min_margin: float = 0.03,
        steps: int = 300,
        batch_size: int = 64,
        seed: int = 0,
    ) -> CalibrationResult:
        """
        Datos:
          - pos_sims: similitudes de pares mismos-IDs (deberían ser altas)
          - neg_sims: similitudes de pares distintos-IDs (deberían ser bajas)

        Loss:
          - Entrenamos un clasificador logístico sobre (sim - threshold)
            y penalizamos min_margin grande (regularización suave).
          - Esto NO entrena ArcFace; solo calibra el "decisor" (post-processing).
        """
        rng = np.random.default_rng(seed)
        pos_sims = np.asarray(pos_sims, dtype=np.float32).reshape(-1)
        neg_sims = np.asarray(neg_sims, dtype=np.float32).reshape(-1)

        theta = np.array([init_threshold, init_min_margin], dtype=np.float32)

        # Fixed slope for logistic; higher => sharper decision boundary.
        k = 25.0
        l2 = 0.02

        for _ in range(steps):
            # SGD-style minibatch sampling (even if using GD optimizer, gradient is still valid).
            p_idx = rng.integers(0, len(pos_sims), size=min(batch_size, len(pos_sims)))
            n_idx = rng.integers(0, len(neg_sims), size=min(batch_size, len(neg_sims)))
            sims = np.concatenate([pos_sims[p_idx], neg_sims[n_idx]], axis=0)
            y = np.concatenate([np.ones(len(p_idx), dtype=np.float32), np.zeros(len(n_idx), dtype=np.float32)], axis=0)

            threshold, min_margin = float(theta[0]), float(theta[1])
            # margin acts as extra strictness: effective threshold = threshold + min_margin
            eff_thr = threshold + min_margin
            z = k * (sims - eff_thr)
            o = self._sigmoid(z)

            eps = 1e-8
            loss = -np.mean(y * np.log(o + eps) + (1.0 - y) * np.log(1.0 - o + eps)) + l2 * (min_margin * min_margin)

            # dL/do then do/dz then dz/dtheta
            dz = (o - y) / max(1, len(y))
            # z = k*(sims - (threshold+min_margin)) => dz/dthreshold = -k ; dz/dmin_margin = -k
            dthreshold = float(np.sum(dz * (-k)))
            dmargin = float(np.sum(dz * (-k)) + (2.0 * l2 * min_margin))
            grad = np.array([dthreshold, dmargin], dtype=np.float32)

            theta = self.opt.step(theta, grad)

            # Keep parameters in reasonable bounds.
            theta[0] = float(np.clip(theta[0], 0.30, 0.95))
            theta[1] = float(np.clip(theta[1], 0.00, 0.20))

        # Final loss estimate on full sets
        eff_thr = float(theta[0] + theta[1])
        sims = np.concatenate([pos_sims, neg_sims], axis=0)
        y = np.concatenate([np.ones_like(pos_sims), np.zeros_like(neg_sims)], axis=0)
        o = self._sigmoid(k * (sims - eff_thr))
        eps = 1e-8
        final_loss = float(-np.mean(y * np.log(o + eps) + (1.0 - y) * np.log(1.0 - o + eps)))

        return CalibrationResult(threshold=float(theta[0]), min_margin=float(theta[1]), loss=final_loss)

