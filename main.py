import sys
import numpy as np
import mss
import time
import time as perf_time
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor, QFont
from pynput import mouse
from collections import deque
import threading
import psutil
import os

p = psutil.Process(os.getpid())
p.nice(psutil.REALTIME_PRIORITY_CLASS)
app = QApplication(sys.argv)
screen_geometry = app.primaryScreen().geometry()
SCREEN_WIDTH = screen_geometry.width()
SCREEN_HEIGHT = screen_geometry.height()
BOX_WIDTH_PERCENT = 0.05
BOX_HEIGHT_PERCENT = 0.05
BOX_LEFT_PERCENT = 0
BOX_TOP_PERCENT = 0.48 
square_size = int(min(SCREEN_WIDTH * BOX_WIDTH_PERCENT, SCREEN_HEIGHT * BOX_HEIGHT_PERCENT))
SCREEN_REGION = {
    'top': int(SCREEN_HEIGHT * BOX_TOP_PERCENT),
    'left': int(SCREEN_WIDTH * BOX_LEFT_PERCENT),
    'width': square_size,
    'height': square_size
}
CHECK_INTERVAL = 0.000001

class LatencyOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(10, 10, 400, 300)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool | Qt.X11BypassWindowManagerHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.init_ui()
        self.reset_latency()

    def init_ui(self):
        self.reset_delay_button = self.create_button('Reset+5s Delay', 250, 200, self.reset_latency_with_delay)
        self.exit_button = self.create_button('Exit', 50, 250, self.exit_application)
        self.reset_button = self.create_button('Reset', 250, 250, self.reset_latency)

    def create_button(self, text, x, y, callback):
        button = QPushButton(text, self)
        button.setGeometry(x, y, 120, 30)
        button.setStyleSheet(self.button_style())
        button.clicked.connect(callback)
        return button
    def init_ui(self):
        self.reset_delay_button = self.create_button('Reset+5s Delay', 250, 200, self.reset_latency_with_delay)
        self.exit_button = self.create_button('Exit', 50, 250, self.exit_application)
        self.reset_button = self.create_button('Reset', 250, 250, self.reset_latency)
        self.toggle_box_button = self.create_button('Toggle Box', 50, 200, self.toggle_box_visibility)

    def toggle_box_visibility(self):
        if box.isVisible():
            box.hide()
        else:
            box.show()

    def button_style(self):
        return """
            QPushButton {
                background-color: #444;
                color: white;
                border: 1px solid #555;
                border-radius: 10px;
                padding: 2px;
            }
            QPushButton:hover {
                background-color: #555;
            }
            QPushButton:pressed {
                background-color: #666;
            }
        """

    def reset_latency(self):
        self.last_latency = 0
        self.avg_latency = 0
        self.min_latency = float('inf')
        self.max_latency = float('-inf')
        latencies.clear()
        self.update()

    def exit_application(self):
        QApplication.quit()

    def reset_latency_with_delay(self):
        self.last_latency = 0
        self.avg_latency = 0
        self.min_latency = float('inf')
        self.max_latency = float('-inf')
        latencies.clear()
        self.update()
        time.sleep(5)
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setOpacity(0.8)
        painter.fillRect(self.rect(), QColor(30, 30, 30))
        painter.setOpacity(1.0)
        painter.setPen(Qt.white)
        font = QFont()
        font.setPointSize(14)
        painter.setFont(font)
        painter.drawText(self.rect().adjusted(10, 10, -10, -50), Qt.AlignLeft | Qt.AlignTop,
                         f"Avg Latency: {self.avg_latency:.2f} ms\n"
                         f"Last: {self.last_latency:.2f} ms\n"
                         f"Min: {self.min_latency:.2f} ms\n"
                         f"Max: {self.max_latency:.2f} ms")

    def update_latency(self, last_latency, avg_latency, min_latency, max_latency):
        self.last_latency = last_latency
        self.avg_latency = avg_latency
        self.min_latency = min_latency
        self.max_latency = max_latency
        self.update()

class BlackBox(QWidget):
    def __init__(self):
        super().__init__()
        self.update_geometry()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.color = QColor(0, 0, 0)
        self.show()

    def update_geometry(self):
        screen_geometry = QApplication.primaryScreen().geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()
        box_width = int(min(screen_width * BOX_WIDTH_PERCENT, screen_height * BOX_HEIGHT_PERCENT))
        box_height = box_width
        box_left = int(screen_width * BOX_LEFT_PERCENT)
        box_top = int(screen_height * BOX_TOP_PERCENT)
        self.setGeometry(box_left, box_top, box_width, box_height)

    def resizeEvent(self, event):
        self.update_geometry()
        super().resizeEvent(event)
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), self.color)

    def turn_white(self):
        self.color = QColor(255, 255, 255)
        self.update()
        threading.Thread(target=self.delayed_turn_black, args=(0.1,)).start()

    def delayed_turn_black(self, delay):
        time.sleep(delay)
        self.color = QColor(0, 0, 0)
        self.update()

def is_white(pixel):
    return np.all(pixel > 200)

def on_click(x, y, button, pressed):
    if pressed:
        click_time = perf_time.perf_counter() - start_time
        clicks.append(click_time)
        print(f"Mouse clicked at {click_time:.6f} seconds")
        box.turn_white()
        global white_detected
        white_detected = False

def watch_screen():
    global start_time, white_time, white_detected
    with mss.mss() as sct:
        start_time = perf_time.perf_counter()
        white_detected = False
        while True:
            screen_geometry = app.primaryScreen().geometry()
            screen_width = screen_geometry.width()
            screen_height = screen_geometry.height()
            square_size = int(min(screen_width * BOX_WIDTH_PERCENT, screen_height * BOX_HEIGHT_PERCENT))
            SCREEN_REGION['top'] = int(screen_height * BOX_TOP_PERCENT)
            SCREEN_REGION['left'] = int(screen_width * BOX_LEFT_PERCENT)
            SCREEN_REGION['width'] = square_size
            SCREEN_REGION['height'] = square_size

            img = np.array(sct.grab(SCREEN_REGION))
            if is_white(img).any() and not white_detected:
                white_time = perf_time.perf_counter() - start_time
                print(f"White detected at {white_time:.6f} seconds")
                white_detected = True
                box.turn_white()
                if clicks:
                    latency = (white_time - clicks[-1]) * 1000
                    latencies.append(latency)
                    print(f"Latency: {latency:.2f} ms")
                    if len(latencies) > 1:
                        avg_latency = sum(latencies) / len(latencies)
                        min_latency = min(latencies)
                        max_latency = max(latencies)
                        print(f"Average Latency: {avg_latency:.2f} ms")
                        print(f"Minimum: {min_latency:.2f} ms")
                        print(f"Maximum: {max_latency:.2f} ms")
                        overlay.update_latency(latency, avg_latency, min_latency, max_latency)
                    clicks.clear()
            elif not is_white(img).any():
                white_detected = False
            time.sleep(CHECK_INTERVAL)

clicks = deque()
latencies = deque()
listener = mouse.Listener(on_click=on_click)
listener.start()
box = BlackBox()
overlay = LatencyOverlay()
overlay.show()
threading.Thread(target=watch_screen, daemon=True).start()
sys.exit(app.exec_())