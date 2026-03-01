# shining_glow_title.py

import sys
import math
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
from PySide6.QtCore import Qt, QTimer, QRectF
from PySide6.QtGui import QPainter, QColor, QLinearGradient, QFont, QPainterPath


class SmoothBlueCyanGlowTitle(QWidget):
    """蓝青渐变发光标题组件，可配置尺寸与字体"""

    def __init__(
        self,
        text: str = "XIAOLAN",
        font_size: int = 18,
        width: int = 270,
        height: int = 70,
        parent=None,
    ):
        super().__init__(parent)
        self.text = text
        self.font_size = font_size
        self.setFixedSize(width, height)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.light_phase = 0.0
        self.glow_phase = 0.0
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self._update_animation)
        self.anim_timer.start(40)

    def _update_animation(self):
        self.light_phase += 0.015
        if self.light_phase > 1.0:
            self.light_phase -= 1.0
        self.glow_phase += 0.08
        if self.glow_phase > 6.28:
            self.glow_phase -= 6.28
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        inner_rect = QRectF(5, 5, w - 10, h - 10)
        light_t = self.light_phase
        if light_t < 0.5:
            color_t = light_t * 2
        else:
            color_t = 2.0 - light_t * 2
        color_blue = (35, 100, 255)  # Bright Blue 60, 180, 255
        color_cyan = (0, 180, 180)  # Cyan 0, 220, 220

        r = int(color_blue[0] * (1 - color_t) + color_cyan[0] * color_t)
        g = int(color_blue[1] * (1 - color_t) + color_cyan[1] * color_t)
        b = int(color_blue[2] * (1 - color_t) + color_cyan[2] * color_t)

        angle_deg = (light_t * 360) % 360
        rad = math.radians(angle_deg)

        dx = math.cos(rad) * w
        dy = math.sin(rad) * h

        gradient = QLinearGradient(w / 2, h / 2, w / 2 + dx, h / 2 + dy)
        gradient.setColorAt(0, QColor(r, g, b))
        gradient.setColorAt(1, QColor(
            int(color_cyan[0] * (1 - color_t) + color_blue[0] * color_t),
            int(color_cyan[1] * (1 - color_t) + color_blue[1] * color_t),
            int(color_cyan[2] * (1 - color_t) + color_blue[2] * color_t)
        ))

        bg_path = QPainterPath()
        bg_path.addRoundedRect(inner_rect, 25, 25)
        painter.fillPath(bg_path, gradient)

        text_rect = QRectF(0, 0, w, h)

        painter.setPen(QColor(255, 255, 255))
        font = QFont("Microsoft YaHei", self.font_size, QFont.Bold)
        painter.setFont(font)
        painter.drawText(text_rect, Qt.AlignCenter, self.text)


# 兼容旧命名
SmoothBlueCyanGlow_title = SmoothBlueCyanGlowTitle


class DemoWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(300, 450)
        self.setStyleSheet("background-color: #0a1929;")

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        self.btn = SmoothBlueCyanGlowTitle("XIAOLAN")
        layout.addWidget(self.btn)

        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DemoWindow()
    window.show()
    sys.exit(app.exec())