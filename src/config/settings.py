from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    # Models
    model_name: str = os.getenv("FR_MODEL_NAME", "buffalo_l")
    model_root: str = os.getenv("FR_MODEL_ROOT", ".")
    det_size: tuple[int, int] = (
        int(os.getenv("FR_DET_W", "640")),
        int(os.getenv("FR_DET_H", "640")),
    )

    # Inference / decision
    metric: str = os.getenv("FR_METRIC", "cosine")
    threshold: float = float(os.getenv("FR_THRESHOLD", "0.60"))
    min_margin: float = float(os.getenv("FR_MIN_MARGIN", "0.03"))
    min_det_score: float = float(os.getenv("FR_MIN_DET_SCORE", "0.50"))
    topk: int = int(os.getenv("FR_TOPK", "1"))

    # Optional Q-learning policy storage
    q_policy_path: str = os.getenv("FR_Q_POLICY_PATH", "data/q_policy.json")

    # Data paths
    data_root: str = os.getenv("FR_DATA_ROOT", "data")
    output_dir: str = os.getenv("FR_OUTPUT_DIR", "output")
