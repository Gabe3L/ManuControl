from typing import Tuple, List

import cv2
import torch
import numpy as np
from ultralytics import YOLO

###############################################################


class ModelTester:
    def __init__(self):
        self.device = torch.device(
            'cuda' if torch.cuda.is_available() else 'cpu')
        self.model = YOLO(
            "video\\train\\weights\\best.engine"
            if torch.cuda.is_available()
            else "video\\train\\weights\\best.onnx",
            task='detect'
        )
        self.confidence_threshold = 0.7

    def detect(self, frame):
        with torch.no_grad():
            results = self.model.predict(frame)[0]
        return self.extract_detections(results)

    @staticmethod
    def annotate_frame(frame, box: Tuple[int, int, int, int], class_id: int):
        return cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), (0, 0, 0), 2)

    def extract_detections(self, results):
        """Extract bounding boxes, confidences, and class IDs."""
        boxes: List[List[int]] = []
        confidences: List[float] = []
        class_ids: List[int] = []

        for box in results.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
            confidence = float(box.conf[0])

            if confidence >= self.confidence_threshold:
                boxes.append([x1, y1, x2, y2])
                confidences.append(confidence)
                class_ids.append(int(box.cls[0]))

        return np.array(boxes), np.array(confidences), np.array(class_ids)

    def process_video(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise RuntimeError("Webcam not found.")

        try:
            while True:
                ret, frame = cap.read()

                if not ret:
                    print("No frame received from webcam.")
                    break

                boxes, confidences, class_ids = self.detect(frame)

                for i, box in enumerate(boxes):
                    frame = self.annotate_frame(frame, box, class_ids[i])

                cv2.imshow("GAIA Test", frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        except Exception as e:
            print(e)
            cap.release()
            cv2.destroyAllWindows()
        finally:
            cap.release()
            cv2.destroyAllWindows()

##############################################################


if __name__ == "__main__":
    tester = ModelTester()
    tester.process_video()
