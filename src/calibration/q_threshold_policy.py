from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from src.algorithms.q_learning import QLearningThresholdPolicy


@dataclass(frozen=True)
class QPolicyResult:
    q_table: list[list[float]]
    bin_edges: list[float]
    actions: list[float]


class QThresholdPolicyTrainer:
    """
    Entrena una política Q-learning (algoritmo 7) para escoger un ajuste al threshold
    basado en el score de similitud (state = bin(similarity)).

    - Estado s: bin de similitud (por ejemplo 0.0-1.0 en 20 bins)
    - Acciones a: offsets a aplicar al threshold: [-0.06, -0.03, 0.0, +0.03, +0.06]
    - Recompensa r: +1 si clasifica correctamente (pos => accept, neg => reject), -1 si no.
    """

    def __init__(self, n_bins: int = 20, actions: list[float] | None = None):
        self.n_bins = n_bins
        self.bin_edges = np.linspace(-1.0, 1.0, n_bins + 1).astype(np.float32)
        self.actions = actions if actions is not None else [-0.06, -0.03, 0.0, 0.03, 0.06]

    def _state(self, sim: float) -> int:
        # returns 0..n_bins-1
        idx = int(np.digitize([sim], self.bin_edges)[0] - 1)
        return max(0, min(self.n_bins - 1, idx))

    def fit(
        self,
        pos_sims: np.ndarray,
        neg_sims: np.ndarray,
        base_threshold: float,
        episodes: int = 2000,
        alpha: float = 0.2,
        gamma: float = 0.95,
        epsilon: float = 0.1,
        seed: int = 0,
    ) -> QPolicyResult:
        rng = np.random.default_rng(seed)
        policy = QLearningThresholdPolicy(
            n_states=self.n_bins,
            n_actions=len(self.actions),
            alpha=alpha,
            gamma=gamma,
            epsilon=epsilon,
        )

        pos_sims = np.asarray(pos_sims, dtype=np.float32).reshape(-1)
        neg_sims = np.asarray(neg_sims, dtype=np.float32).reshape(-1)

        for _ in range(episodes):
            is_pos = bool(rng.integers(0, 2))
            sim = float(pos_sims[rng.integers(0, len(pos_sims))]) if is_pos else float(neg_sims[rng.integers(0, len(neg_sims))])
            state = self._state(sim)

            action = policy.act(state)
            thr = base_threshold + float(self.actions[action])
            pred_pos = sim >= thr
            reward = 1.0 if (pred_pos == is_pos) else -1.0

            # stateless task; next_state = current bin
            next_state = state
            policy.update(state, action, reward, next_state)

        return QPolicyResult(
            q_table=policy.q.tolist(),
            bin_edges=[float(x) for x in self.bin_edges.tolist()],
            actions=[float(a) for a in self.actions],
        )

