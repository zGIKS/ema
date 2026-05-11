import cv2
import numpy as np
from pathlib import Path
from typing import Optional, Tuple

class OutputLayer:
    def __init__(self, output_dir: Path = Path("output")):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def print_console(self, name: Optional[str], confidence: float, recognized: bool):
        if recognized:
            print(f"\n[OK] Person detected: {name}")
            print(f"   Confidence: {confidence*100:.2f}%")
        else:
            print(f"\n[FAIL] Unknown person")
            if name is None:
                print("   Best match: N/A")
            else:
                print(f"   Best match: {name} ({confidence*100:.2f}%) (threshold not met)")

    def draw_results(self, image_path: Path, detections: list) -> Optional[Path]:
        """
        detections: list of dicts with keys:
          - bbox: (x1,y1,x2,y2)
          - label: str
          - recognized: bool
        """
        img = cv2.imread(str(image_path))
        if img is None or not detections:
            return None

        for det in detections:
            x1, y1, x2, y2 = map(int, det["bbox"])
            recognized = bool(det.get("recognized", False))
            label = str(det.get("label", "Unknown"))
            color = (0, 255, 0) if recognized else (0, 0, 255)

            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
            cv2.putText(img, label, (x1, max(0, y1 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        out_path = self.output_dir / f"{image_path.stem}_result.jpg"
        cv2.imwrite(str(out_path), img)
        print(f"[IMG] Result image saved to: {out_path}")
        return out_path
