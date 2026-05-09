from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class QPolicyOnDisk:
    q_table: list[list[float]]
    bin_edges: list[float]
    actions: list[float]


class PolicyStore:
    def __init__(self, path: Path):
        self.path = path

    def save_q_policy(self, policy: QPolicyOnDisk) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(asdict(policy), indent=2), encoding="utf-8")

    def load_q_policy(self) -> QPolicyOnDisk | None:
        if not self.path.exists():
            return None
        obj = json.loads(self.path.read_text("utf-8"))
        return QPolicyOnDisk(
            q_table=obj["q_table"],
            bin_edges=obj["bin_edges"],
            actions=obj["actions"],
        )

