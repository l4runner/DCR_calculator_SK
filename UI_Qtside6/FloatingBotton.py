from PySide6.QtWidgets import QGraphicsDropShadowEffect, QPushButton
from PySide6.QtCore import QPropertyAnimation, QEasingCurve, QPoint, Qt, QTimer, Signal, QSize
from PySide6.QtGui import QFont, QColor, QIcon


class FloatingLabel_Btn(QPushButton):

    def __init__(self, text="", icon_path=None, parent=None):
        super().__init__(parent)
        self.text = text
        self.icon_path = icon_path

        self.init_ui()

        self.setFont(QFont("Arial", 16))
        self.setStyleSheet("""
            QPushButton {
                background-color: #45475a; 
                color: #cdd6f4;
                padding: 10px; 
                border-radius: 5px;
                text-align: center;
                spacing: 8px;
            }
            QPushButton:hover {
                background-color: #585b70;
            }
        """)

        self.setCursor(Qt.PointingHandCursor)
        self.original_pos = None
        self.pos_animation = QPropertyAnimation(self, b"pos")
        self.pos_animation.setDuration(200)
        self.pos_animation.setEasingCurve(QEasingCurve.OutCubic)

        self.shadow = None
        self.shadow_timer = QTimer()
        self.shadow_timer.setSingleShot(False)
        self.shadow_timer.timeout.connect(self.update_shadow_opacity)

        self.current_shadow_alpha = 0
        self.is_fading_out = False

    def init_ui(self):
        if self.icon_path:
            self.setIcon(QIcon(self.icon_path))
            self.setIconSize(QSize(25, 25))

            self.setText(f"  {self.text}")
        else:
            self.setText(self.text)

    def set_icon(self, icon_path):
        self.icon_path = icon_path
        if icon_path:
            self.setIcon(QIcon(icon_path))
            self.setIconSize(QSize(25, 25))
            self.setText(f"  {self.text}")
        else:
            self.setIcon(QIcon())
            self.setText(self.text)

    def enterEvent(self, event):
        if self.original_pos is None:
            self.original_pos = self.pos()

        self.animate_position(self.original_pos - QPoint(0, 10))
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self.original_pos is not None:
            self.animate_position(self.original_pos)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if self.original_pos is not None:
            self.animate_position(self.original_pos + QPoint(0, 5))
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        target = self.original_pos - QPoint(0, 10) if self.underMouse() else self.original_pos
        self.animate_position(target)

        self.clicked.emit()

        self.show_shadow()

        super().mouseReleaseEvent(event)

    def animate_position(self, pos):
        self.pos_animation.stop()
        self.pos_animation.setStartValue(self.pos())
        self.pos_animation.setEndValue(pos)
        self.pos_animation.start()

    def show_shadow(self):
        if self.shadow is None:
            self.shadow = QGraphicsDropShadowEffect()
            self.shadow.setColor(QColor(255, 255, 255, 220))
            self.shadow.setBlurRadius(35)
            self.shadow.setOffset(0, 8)

        self.setGraphicsEffect(self.shadow)

        self.current_shadow_alpha = 220
        self.is_fading_out = False
        self.shadow.setColor(QColor(255, 255, 255, self.current_shadow_alpha))

        self.shadow_timer.start(50)

    def update_shadow_opacity(self):
        if self.shadow and self.current_shadow_alpha > 0:
            self.current_shadow_alpha -= 20

            if self.current_shadow_alpha < 0:
                self.current_shadow_alpha = 0
                self.shadow_timer.stop()
                self.setGraphicsEffect(None)
            else:
                self.shadow.setColor(QColor(255, 255, 255, self.current_shadow_alpha))
        else:
            self.shadow_timer.stop()
