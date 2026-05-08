import cv2
import numpy as np
from pathlib import Path

class PreprocessingLayer:
    def __init__(self, target_size: tuple = (640, 640)):
        self.target_size = target_size

    def load_image(self, image_path: Path) -> np.ndarray:
        img = cv2.imread(str(image_path))
        if img is None:
            raise ValueError(f"Could not load image: {image_path}")
        return img

    def resize_if_needed(self, img: np.ndarray, max_dim: int = 1920) -> np.ndarray:
        h, w = img.shape[:2]
        if max(h, w) > max_dim:
            scale = max_dim / max(h, w)
            new_size = (int(w * scale), int(h * scale))
            img = cv2.resize(img, new_size, interpolation=cv2.INTER_AREA)
        return img

    def clean_image(self, img: np.ndarray) -> np.ndarray:
        return cv2.fastNlMeansDenoisingColored(img, None, 5, 5, 7, 21)

    def to_rgb(self, img: np.ndarray) -> np.ndarray:
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    def process(self, image_path: Path, denoise: bool = False) -> np.ndarray:
        img = self.load_image(image_path)
        img = self.resize_if_needed(img)
        if denoise:
            img = self.clean_image(img)
        img = self.to_rgb(img)
        return img
