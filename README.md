# ManuControl

**ManuControl**, derived from the Latin word for hand, "manus,” is a cutting-edge gesture recognition system that allows users to control their operating system using hand gestures. Built with **YOLOv11** for real-time hand tracking and gesture detection, ManuControl offers a seamless, touchless control interface designed for productivity, accessibility, and futuristic human-computer interaction.

---

## Features

- Real-time hand gesture recognition
- Gesture-based mouse movement and clicks
- Optional gesture-based authentication
- Low-latency performance (under 50ms)

---

## Supported Gestures

| Gesture            | Action          |
| ------------------ | --------------- |
| ✋ Open palm       | Cursor control  |
| 👊 Fist            | Ignore Hand     |
| 👌 Fingers Pinched | Left click      |
| ✌️ Two fingers     | Right Click     |
| 👍 Thumbs up       | Scroll up       |
| 👎 Thumbs down     | Scroll down     |
| 🤙 Pinky and Thumb | Open Start Menu |

---

## Installation

### Requirements

- Python
- Webcam or External Camera

### Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/manucontrol.git
   cd manucontrol
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:
   ```bash
   python -m main.py
   ```

# Author

### Gabe Lynch

Website: https://www.gabelynch.com \
GitHub: https://github.com/Gabe3L \
Email: contact@gabelynch.com

# License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) in the root of this project for more details.
