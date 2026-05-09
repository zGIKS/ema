from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    # Models
    model_name: str = "buffalo_l"
    model_root: str = "."
    det_size: tuple[int, int] = (640, 640)

    # Inference / decision
    metric: str = "cosine"
    threshold: float = 0.60
    min_margin: float = 0.03
    min_det_score: float = 0.50
    topk: int = 1

    # Optional Q-learning policy storage
    q_policy_path: str = "data/q_policy.json"

    # Data paths
    data_root: str = "data"
    output_dir: str = "output"

    # Data layout
    # Default is folder-per-person: data/known_people/<person_name>/*.jpg
    # Set FR_ALLOW_FLAT_KNOWN=1 to also accept images directly under known_people/
    allow_flat_known_people: bool = False

    @classmethod
    def from_env(cls) -> "Settings":
        truthy = {"1", "true", "TRUE", "yes", "YES", "on", "ON"}

        det_w = int(os.getenv("FR_DET_W", "640"))
        det_h = int(os.getenv("FR_DET_H", "640"))

        return cls(
            model_name=os.getenv("FR_MODEL_NAME", cls.model_name),
            model_root=os.getenv("FR_MODEL_ROOT", cls.model_root),
            det_size=(det_w, det_h),
            metric=os.getenv("FR_METRIC", cls.metric),
            threshold=float(os.getenv("FR_THRESHOLD", str(cls.threshold))),
            min_margin=float(os.getenv("FR_MIN_MARGIN", str(cls.min_margin))),
            min_det_score=float(os.getenv("FR_MIN_DET_SCORE", str(cls.min_det_score))),
            topk=int(os.getenv("FR_TOPK", str(cls.topk))),
            q_policy_path=os.getenv("FR_Q_POLICY_PATH", cls.q_policy_path),
            data_root=os.getenv("FR_DATA_ROOT", cls.data_root),
            output_dir=os.getenv("FR_OUTPUT_DIR", cls.output_dir),
            allow_flat_known_people=os.getenv("FR_ALLOW_FLAT_KNOWN", "0") in truthy,
        )
