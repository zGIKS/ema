from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class QLearningThresholdPolicy:
    """
    ## 7. Reinforcement Learning (Q-Learning)

    Aprende una política para ajustar el umbral (threshold) según un estado discreto.

    Update:
      Q(s,a) = Q(s,a) + alpha * [ r + gamma * max_a' Q(s',a') - Q(s,a) ]

    En este repo lo usamos como política opcional para "ajustar" el threshold de forma
    simple según el estado (bins de det_score y tamaño de cara). Útil cuando quieres
    ser más estricto con caras pequeñas/dudosas y menos estricto con caras grandes/nítidas.
    """

    n_states: int
    n_actions: int
    alpha: float = 0.2
    gamma: float = 0.95
    epsilon: float = 0.1

    def __post_init__(self) -> None:
        self.q = np.zeros((self.n_states, self.n_actions), dtype=np.float32)

    def act(self, state: int) -> int:
        if np.random.rand() < self.epsilon:
            return int(np.random.randint(0, self.n_actions))
        return int(np.argmax(self.q[state]))

    def update(self, state: int, action: int, reward: float, next_state: int) -> None:
        best_next = float(np.max(self.q[next_state]))
        td_target = reward + self.gamma * best_next
        td_error = td_target - float(self.q[state, action])
        self.q[state, action] = float(self.q[state, action] + self.alpha * td_error)

