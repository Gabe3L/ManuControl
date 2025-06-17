from typing import Tuple, List

import torch
import numpy as np
from ultralytics import YOLO

from config import VideoConfig

###############################################################


class YOLODetector:
    def __init__(self) -> None:
        self.device: torch.device = torch.device(
            'cuda' if torch.cuda.is_available() else 'cpu')
        self.model: YOLO = YOLO("train\\weights\\best.engine" if torch.cuda.is_available(
        ) else "train\\weights\\best.onnx", task='detect')
        self.confidence_threshold: float = VideoConfig.CONFIDENCE_THRESHOLD

    def detect(self, frame: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        with torch.no_grad():
            results = self.model.predict(frame)[0]
        return self.extract_detections(results)

    def extract_detections(self, results) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        boxes: List[List[int]] = []
        confidences: List[float] = []
        class_ids: List[int] = []

        for box in results.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
            confidence: float = float(box.conf[0])

            if confidence >= self.confidence_threshold:
                boxes.append([x1, y1, x2, y2])
                confidences.append(confidence)
                class_ids.append(int(box.cls[0]))

        return np.array(boxes), np.array(confidences), np.array(class_ids)