from dataclasses import dataclass
import numpy as np

from .backprop import LogisticNeuron
from .optimizers import Adam, GradientDescent, Momentum, StochasticGradientDescent


@dataclass(frozen=True)
class LogisticCalibratorResult:
    w: list[float]
    b: float
    loss: float


class LogisticCalibrator:
    def __init__(self, optimizer: str = "adam", lr: float = 0.1):
        name = optimizer.lower()
        if name == "gd":
            self.opt = GradientDescent(lr=lr)
        elif name == "sgd":
            self.opt = StochasticGradientDescent(lr=lr)
        elif name == "momentum":
            self.opt = Momentum(lr=lr, gamma=0.9)
        elif name == "adam":
            self.opt = Adam(lr=lr)
        else:
            raise ValueError("optimizer must be one of: gd, sgd, momentum, adam")

    def fit(self, pos_sims: np.ndarray, neg_sims: np.ndarray,
            steps: int = 400, seed: int = 0) -> LogisticCalibratorResult:
        rng = np.random.default_rng(seed)
        pos_sims = np.asarray(pos_sims, dtype=np.float32).reshape(-1)
        neg_sims = np.asarray(neg_sims, dtype=np.float32).reshape(-1)

        sims = np.concatenate([pos_sims, neg_sims], axis=0)
        y = np.concatenate([np.ones_like(pos_sims), np.zeros_like(neg_sims)], axis=0)

        idx = rng.permutation(len(sims))
        sims = sims[idx]
        y = y[idx]

        x = np.stack([sims, np.ones_like(sims)], axis=1)
        neuron = LogisticNeuron(w=np.zeros(2, dtype=np.float32), b=0.0)

        params = np.array([neuron.w[0], neuron.w[1], neuron.b], dtype=np.float32)

        for _ in range(steps):
            loss, dw, db = neuron.loss_and_grad(x, y)
            grad = np.array([dw[0], dw[1], db], dtype=np.float32)
            params = self.opt.step(params, grad)
            neuron.w = params[:2].astype(np.float32)
            neuron.b = float(params[2])

        final_loss, _, _ = neuron.loss_and_grad(x, y)
        return LogisticCalibratorResult(w=[float(neuron.w[0]), float(neuron.w[1])],
                                        b=float(neuron.b), loss=float(final_loss))