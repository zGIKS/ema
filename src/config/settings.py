from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    # Models
    model_name: str = "buffalo_l"
    model_root: str = "."
    det_size: tuple[int, int] = (640, 640)

    # Inference / decision
    metric: str = "cosine"
    threshold: float = 0.80
    min_margin: float = 0.03
    min_det_score: float = 0.50
    topk: int = 1

    # Optional Q-learning policy storage
    q_policy_path: str = "data/q_policy.json"

    # Data paths
    data_root: str = "data"
    output_dir: str = "output"
