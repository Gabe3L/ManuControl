class VideoConfig:
    GUI_ENABLED: bool = True
    CONFIDENCE_THRESHOLD: float = 0.6

    LEFT_CLICK_DELAY: float = 1.5
    RIGHT_CLICK_DELAY: float = 2.0
    FPS_SMOOTHING_FACTOR: int = 25
    UPDATE_INTERVAL: float = 0.05

    ROTATE_IMAGE: bool = False
    FLIP_IMAGE_HORIZONTALLY: bool = False
    FLIP_IMAGE_VERTICALLY: bool = False

    CONFIDENCE_THRESHOLD: float = 0.6
    MAX_CAMERA_LOAD_ATTEMPTS: int = 500

    LABEL_COLOURS = {
        0: (0, 0, 255),
        1: (208, 224, 64),
        2: (0, 255, 255),
        3: (203, 192, 255),
        4: (255, 0, 255),
        5: (0, 225, 0),
        6: (0, 165, 225)
    }
    LABELS = {
        0: 'hand_closed',
        1: 'hand_open',
        2: 'hand_pinching',
        3: 'three_fingers_down',
        4: 'thumbs_down',
        5: 'thumbs_up',
        6: 'two_fingers_up',
    }
