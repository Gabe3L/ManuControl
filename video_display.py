import cv2
import numpy as np
from typing import List

from config import VideoConfig


class VideoDisplay:
    @staticmethod
    def show_frame(window_name: str, frame: np.ndarray) -> None:
        """Displays the frame in a window."""
        cv2.imshow(window_name, frame)

    @staticmethod
    def annotate_frame(frame: np.ndarray, box: List[int], class_id: int) -> np.ndarray:
        """Annotate the frame with bounding boxes and labels."""
        color = VideoConfig.LABEL_COLOURS.get(class_id, (255, 255, 255))
        return cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), color, 2)

    @staticmethod
    def insert_text_onto_frame(frame: np.ndarray, message: str, row: int) -> np.ndarray:
        """Annotate the frane with text"""
        if message:
            cv2.putText(frame, message, (10, (30 + (row * 50))),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)
        
        return frame