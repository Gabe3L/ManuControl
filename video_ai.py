import time
import logging
import asyncio
from threading import Lock, Thread
from typing import List, Optional, Tuple

import cv2
import numpy as np
import torch

from video_detector import YOLODetector
from video_display import VideoDisplay
from windows_control import Windows
from fps_tracker import FPSTracker

from config import VideoConfig

################################################################


class Webcam:
    def __init__(self) -> None:
        self.cap = self.load_webcam()
        self.windows = Windows()
        self.device = torch.device(
            'cuda' if torch.cuda.is_available() else 'cpu')
        self.model: YOLODetector = YOLODetector()
        self.fps_tracker = FPSTracker()

        self.screen_res = self.windows.get_screen_res()
        self.camera_res = (int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                           int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        self.webcam_to_screen_ratio = self.windows.get_webcam_to_screen_ratio(
            self.screen_res, self.camera_res)
        
        self.last_left_click_time: float = 0.0
        self.last_right_click_time: float = 0.0
        self.frame: Optional[np.ndarray] = None
        self.frame_lock = Lock()

        self.camera_thread_running = True
        self.camera_thread = Thread(target=self.update_frame, daemon=True)
        self.camera_thread.start()

    def load_webcam(self) -> cv2.VideoCapture:
        cap = None
        for _ in range(5):
            cap = cv2.VideoCapture(0)
            if cap.isOpened():
                break
            else:
                time.sleep(0.002)
        if cap is None or not cap.isOpened():
            logging.warning("Webcam not found.")
            raise RuntimeError("Webcam initialization failed.")
        return cap

    def update_frame(self):
        while self.camera_thread_running:
            ret, frame = self.cap.read()
            if ret:
                with self.frame_lock:
                    self.frame = frame

    def transform_frame(self, frame: np.ndarray) -> np.ndarray:
        if VideoConfig.ROTATE_IMAGE:
            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        if VideoConfig.FLIP_IMAGE_HORIZONTALLY:
            frame = cv2.flip(frame, 1)
        if VideoConfig.FLIP_IMAGE_VERTICALLY:
            frame = cv2.flip(frame, 0)

        return frame

    def most_confident_box(self, boxes: List[List[int]], confidences: List[float], class_ids: List[int]) -> Optional[Tuple[List[int], int]]:
        if not confidences:
            return None

        max_index = np.argmax(confidences)
        box = boxes[max_index]
        label = class_ids[max_index]

        return box, label

    def find_box_center(self, box: List[int]) -> Tuple[int, int]:
        x0, y0, x1, y1 = box
        x = (x0 + x1) // 2
        y = (y0 + y1) // 2

        x = max(
            0, min(int(x * self.webcam_to_screen_ratio[0]), self.screen_res[0] - 1))
        y = max(
            0, min(int(y * self.webcam_to_screen_ratio[1]), self.screen_res[1] - 1))

        return x, y

    async def process_video(self) -> None:
        attempts: int = 0
        while (self.frame is None) and (attempts < VideoConfig.MAX_CAMERA_LOAD_ATTEMPTS):
            await asyncio.sleep(0.01)
            attempts += 1

        try:
            while True:
                with self.frame_lock:
                    frame = self.frame.copy() if self.frame is not None else None

                if frame is None:
                    logging.warning("No frame received from webcam.")
                    break

                frame = self.transform_frame(frame)

                boxes, confidences, class_ids = self.model.detect(frame)
                detection = self.most_confident_box(boxes.tolist(), confidences.tolist(), class_ids.tolist())
                box, label = detection if detection else (None, None)

                if box is not None and label is not None:
                    await self.perform_action(box, label)
                    frame = VideoDisplay.annotate_frame(frame, box, label)

                self.fps_tracker.update()

                frame = VideoDisplay.insert_text_onto_frame(frame, f'FPS: {self.fps_tracker.displayed_fps:.1f}', row=1)
                VideoDisplay.show_frame("GAIA Test", frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

                await asyncio.sleep(0)
        finally:
            self.camera_thread_running = False
            self.camera_thread.join()
            self.cap.release()
            if VideoConfig.GUI_ENABLED:
                cv2.destroyAllWindows()

    async def perform_action(self, box: List[int], class_id: int) -> None:
        label: str = VideoConfig.LABELS[class_id]
        x, y = self.find_box_center(box)

        match label:
            case 'hand_open':
                await self.windows.left_mouse_up()
                await self.windows.move_mouse(x, y)
                return

            case 'hand_closed':
                await self.windows.left_mouse_up()
                return

            case 'hand_pinching':
                self.windows.clicking = True
                await self.windows.move_mouse(x, y)
                await self.windows.left_mouse_down()
                return

            case 'two_fingers_up':
                await self.windows.move_mouse(x, y)
                await self.windows.right_mouse_click()
                return

            case 'thumbs_up':
                await self.windows.left_mouse_up()
                await self.windows.mouse_scroll('up')
                return

            case 'thumbs_down':
                await self.windows.left_mouse_up()
                await self.windows.mouse_scroll('down')
                return
            
            case 'three_fingers_down':
                await self.windows.open_start_menu()
                return