from dataclasses import dataclass
import numpy as np


@dataclass
class QLearningThresholdPolicy:
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