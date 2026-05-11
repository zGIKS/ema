from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from .optimizers import Adam, GradientDescent, Momentum, StochasticGradientDescent


@dataclass(frozen=True)
class CalibrationResult:
    threshold: float
    min_margin: float
    loss: float


class ThresholdCalibrator:
    def __init__(self, optimizer: str = "adam", lr: float = 0.05):
        opts = {"gd": GradientDescent, "sgd": StochasticGradientDescent,
                "momentum": Momentum, "adam": Adam}
        if optimizer.lower() not in opts:
            raise ValueError("optimizer must be one of: gd, sgd, momentum, adam")
        self.opt = opts[optimizer.lower()](lr=lr)

    @staticmethod
    def _sigmoid(z: np.ndarray) -> np.ndarray:
        return 1.0 / (1.0 + np.exp(-z))

    def fit(self, pos_sims: np.ndarray, neg_sims: np.ndarray,
            init_threshold: float = 0.80, init_min_margin: float = 0.03,
            steps: int = 300, batch_size: int = 64, seed: int = 0) -> CalibrationResult:
        rng = np.random.default_rng(seed)
        pos_sims = np.asarray(pos_sims, dtype=np.float32).reshape(-1)
        neg_sims = np.asarray(neg_sims, dtype=np.float32).reshape(-1)

        theta = np.array([init_threshold, init_min_margin], dtype=np.float32)
        k, l2 = 25.0, 0.02

        for _ in range(steps):
            p_idx = rng.integers(0, len(pos_sims), size=min(batch_size, len(pos_sims)))
            n_idx = rng.integers(0, len(neg_sims), size=min(batch_size, len(neg_sims)))
            sims = np.concatenate([pos_sims[p_idx], neg_sims[n_idx]], axis=0)
            y = np.concatenate([np.ones(len(p_idx)), np.zeros(len(n_idx))], axis=0).astype(np.float32)

            eff_thr = float(theta[0] + theta[1])
            o = self._sigmoid(k * (sims - eff_thr))

            eps, loss = 1e-8, -np.mean(y * np.log(o + eps) + (1 - y) * np.log(1 - o + eps))
            loss += l2 * theta[1] * theta[1]

            dz = (o - y) / max(1, len(y))
            grad = np.array([-k * np.sum(dz), -k * np.sum(dz) + 2.0 * l2 * theta[1]], dtype=np.float32)
            theta = self.opt.step(theta, grad)
            theta[0] = float(np.clip(theta[0], 0.30, 0.95))
            theta[1] = float(np.clip(theta[1], 0.00, 0.20))

        eff_thr = float(theta[0] + theta[1])
        sims = np.concatenate([pos_sims, neg_sims])
        y = np.concatenate([np.ones_like(pos_sims), np.zeros_like(neg_sims)])
        o = self._sigmoid(k * (sims - eff_thr))
        final_loss = float(-np.mean(y * np.log(o + 1e-8) + (1 - y) * np.log(1 - o + 1e-8)))

        return CalibrationResult(threshold=float(theta[0]), min_margin=float(theta[1]), loss=final_loss)