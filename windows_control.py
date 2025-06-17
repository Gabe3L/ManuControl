import math
import ctypes
import asyncio
from typing import Tuple
from functools import wraps
from threading import Timer, Lock

def cooldown(cooldown_seconds: float, one_run: bool = True):
    def decorator(func):
        lock = Lock()
        cooldown_active = False
        cooldown_timer = None

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            nonlocal cooldown_active, cooldown_timer

            with lock:
                if cooldown_active:
                    return None
                
                result = func(self, *args, **kwargs)

                def reset_cooldown():
                    nonlocal cooldown_active
                    with lock:
                        cooldown_active = False
                
                if one_run:
                    cooldown_active = True
                    cooldown_timer = Timer(cooldown_seconds, reset_cooldown)
                    cooldown_timer.start()

                else:
                    if cooldown_timer is not None:
                        cooldown_timer.cancel()
                    cooldown_active = True
                    cooldown_timer = Timer(cooldown_seconds, reset_cooldown)
                    cooldown_timer.start()

                return result
        return wrapper
    return decorator

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


class RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long),
                ("top", ctypes.c_long),
                ("right", ctypes.c_long),
                ("bottom", ctypes.c_long)]


class Windows:
    MOUSEEVENTF_LEFTDOWN = 0x0002
    MOUSEEVENTF_LEFTUP = 0x0004
    MOUSEEVENTF_WHEEL = 0x0800
    MOUSEEVENTF_RIGHTDOWN = 0x0008
    MOUSEEVENTF_RIGHTUP = 0x0010
    KEYEVENTF_KEYDOWN = 0x0000
    KEYEVENTF_KEYUP = 0x0002
    VK_LWIN = 0x5B

    def __init__(self) -> None:
        self.clicking = False
        self.mci = ctypes.WinDLL('winmm')
        self.user32 = ctypes.windll.user32

    def get_cursor_pos(self) -> Tuple[int, int]:
        point = POINT()
        self.user32.GetCursorPos(ctypes.byref(point))
        return point.x, point.y

    def get_screen_res(self) -> Tuple[int, int]:
        return (self.user32.GetSystemMetrics(0), self.user32.GetSystemMetrics(1))

    def get_webcam_to_screen_ratio(self, screen_res: Tuple[int, int], camera_res: Tuple[int, int]) -> Tuple[float, float]:
        return (screen_res[0] / screen_res[1], camera_res[0] / camera_res[1])

    def mouse_event(self, dwFlags: int, dx: int = 0, dy: int = 0, dwData: int = 0, dwExtraInfo: int = 0) -> None:
        self.user32.mouse_event(dwFlags, dx, dy, dwData, dwExtraInfo)

    async def move_mouse(self, end_x: int, end_y: int) -> None:
        start_x, start_y = self.get_cursor_pos()

        dx = end_x - start_x
        dy = end_y - start_y
        steps = max(int(math.hypot(dx, dy)), 1)
        step_x = dx / steps
        step_y = dy / steps

        for i in range(steps):
            x = int(start_x + step_x * i)
            y = int(start_y + step_y * i)
            self.user32.SetCursorPos(int(x), int(y))
        self.user32.SetCursorPos(int(end_x), int(end_y))

    async def mouse_scroll(self, direction: str) -> None:
        directions = {'up': 100, 'down': -100}
        self.mouse_event(self.MOUSEEVENTF_WHEEL, dwData=directions[direction])

    @cooldown(1.5, one_run=False)
    async def left_mouse_down(self) -> None:
        self.mouse_event(self.MOUSEEVENTF_LEFTDOWN)

    async def left_mouse_up(self) -> None:
        if self.clicking:
            self.mouse_event(self.MOUSEEVENTF_LEFTUP)
            self.clicking = False

    @cooldown(2.0, one_run=True)
    async def right_mouse_click(self) -> None:
        self.mouse_event(self.MOUSEEVENTF_RIGHTDOWN)
        await asyncio.sleep(0.05)
        self.mouse_event(self.MOUSEEVENTF_RIGHTUP)

    @cooldown(2.0, one_run=True)
    async def open_start_menu(self) -> None:
        ctypes.windll.user32.keybd_event(self.VK_LWIN, 0, self.KEYEVENTF_KEYDOWN, 0)
        await asyncio.sleep(0.05)
        ctypes.windll.user32.keybd_event(self.VK_LWIN, 0, self.KEYEVENTF_KEYUP, 0)