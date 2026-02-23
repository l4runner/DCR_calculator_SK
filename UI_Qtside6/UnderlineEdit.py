from PySide6.QtCore import QPoint, QRect, QPropertyAnimation, QEasingCurve, Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLineEdit, QFrame, QLabel
from PySide6.QtGui import QFont
import sys


class FloatingLabel_input(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("color: #585b70; font-size: 14px; background: transparent;")
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.hide()

        self.float_animation = QPropertyAnimation(self, b"pos")
        self.float_animation.setDuration(300)
        self.float_animation.setEasingCurve(QEasingCurve.OutCubic)

    def move_to(self, target_pos):
        self.float_animation.stop()
        self.float_animation.setStartValue(self.pos())
        self.float_animation.setEndValue(target_pos)
        self.float_animation.start()


class UnderlineEdit(QLineEdit):
    def __init__(self, placeholder_text="", parent=None):
        super().__init__(parent)
        self.placeholder_text = placeholder_text
        self.container_parent = parent
        if self.container_parent is None:
            raise ValueError("UnderlineEdit requires a layout container as parent.")

        self.setFixedHeight(40)
        self.setStyleSheet("""
            QLineEdit {
                background-color: transparent;
                border: none;
                border-bottom: 2px solid #585b70;
                color: #cdd6f4;
                padding: 8px 0 6px 0;   /* 上少下多，视觉下沉 */
                font-size: 14px;
            }
        """)

        self.setTextMargins(0, 12, 0, 0)
        self.floating_label = FloatingLabel_input(placeholder_text, self.container_parent)
        self.indicator_line = QFrame(self.container_parent)
        self.indicator_line.setStyleSheet("background-color: #89b4fa;")
        self.indicator_line.setFixedHeight(2)
        self.indicator_line.hide()
        self.textChanged.connect(self.on_text_changed)

        self.line_animation = QPropertyAnimation(self.indicator_line, b"geometry")
        self.line_animation.setDuration(300)
        self.line_animation.setEasingCurve(QEasingCurve.OutCubic)

        self.has_text = False
        self.is_focused = False

        self.update_floating_label_position()

    def update_floating_label_position(self):
        if not self.container_parent:
            return
        pos = self.mapTo(self.container_parent, QPoint(0, 0))
        label_height = self.floating_label.sizeHint().height()

        if self.has_text or self.is_focused:
            target_y = pos.y() - 5
            self.floating_label.setStyleSheet("color: #89b4fa; font-size: 12px; background: transparent;")
        else:
            target_y = pos.y() + (self.height() - label_height) // 2 + 2
            self.floating_label.setStyleSheet("color: #585b70; font-size: 14px; background: transparent;")

        self.floating_label.move(pos.x(), target_y)
        self.floating_label.show()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_floating_label_position()
        if not self.indicator_line.isHidden():
            pos = self.mapTo(self.container_parent, QPoint(0, 0))
            self.indicator_line.setGeometry(pos.x(), pos.y() + self.height() - 1, self.width(), 2)

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.is_focused = True
        self.show_indicator_line()
        if not self.has_text:
            self.animate_label_up()
        try:
            self.line_animation.finished.disconnect()
        except:
            pass
        self.line_animation.finished.connect(self.on_show_animation_finished)

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.is_focused = False
        self.setStyleSheet("""
            QLineEdit {
                background-color: transparent;
                border: none;
                border-bottom: 2px solid #585b70;
                color: #cdd6f4;
                padding: 8px 0 6px 0;
                font-size: 14px;
            }
        """)
        self.hide_indicator_line()
        if not self.text():
            self.has_text = False
            self.animate_label_down()

    def on_text_changed(self, text):
        if text and not self.has_text:
            self.has_text = True
            if not self.is_focused:
                self.animate_label_up()
        elif not text and not self.is_focused:
            self.has_text = False
            self.animate_label_down()
        self.update_floating_label_position()

    def animate_label_up(self):
        if not self.container_parent:
            return
        pos = self.mapTo(self.container_parent, QPoint(0, 0))
        target_pos = QPoint(pos.x(), pos.y() - 5)
        self.floating_label.move_to(target_pos)
        self.floating_label.setStyleSheet("color: #89b4fa; font-size: 12px; background: transparent;")

    def animate_label_down(self):
        if not self.container_parent:
            return
        pos = self.mapTo(self.container_parent, QPoint(0, 0))
        label_height = self.floating_label.sizeHint().height()
        target_y = pos.y() + (self.height() - label_height) // 2 + 2  # +2 对齐下沉光标
        target_pos = QPoint(pos.x(), target_y)
        self.floating_label.move_to(target_pos)
        self.floating_label.setStyleSheet("color: #585b70; font-size: 14px; background: transparent;")

    def show_indicator_line(self):
        if not self.container_parent:
            return
        pos = self.mapTo(self.container_parent, QPoint(0, 0))
        self.indicator_line.setGeometry(pos.x(), pos.y() + self.height() - 1, 0, 2)
        self.indicator_line.show()
        self.line_animation.setStartValue(QRect(pos.x(), pos.y() + self.height() - 1, 0, 2))
        self.line_animation.setEndValue(QRect(pos.x(), pos.y() + self.height() - 1, self.width(), 2))
        self.line_animation.start()

    def hide_indicator_line(self):
        if self.indicator_line.isHidden():
            return
        pos = self.mapTo(self.container_parent, QPoint(0, 0))
        self.line_animation.setStartValue(QRect(pos.x(), pos.y() + self.height() - 1, self.width(), 2))
        self.line_animation.setEndValue(QRect(pos.x(), pos.y() + self.height() - 1, 0, 2))
        self.line_animation.start()
        try:
            self.line_animation.finished.disconnect()
        except:
            pass
        self.line_animation.finished.connect(lambda: self.indicator_line.hide())

    def on_show_animation_finished(self):
        try:
            self.line_animation.finished.disconnect(self.on_show_animation_finished)
        except:
            pass
        self.setStyleSheet("""
            QLineEdit {
                background-color: transparent;
                border: none;
                border-bottom: 2px solid #89b4fa;
                color: #cdd6f4;
                padding: 8px 0 6px 0;
                font-size: 14px;
            }
        """)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Material Design Input (Fixed Clipping + Cursor Alignment)")
        self.setGeometry(100, 100, 400, 320)
        self.setStyleSheet("background-color: #1e1e2e;")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(30)

        inputs_data = ["参考料号", "线圈规格", "目标料号", "DCR(TYP)"]
        for placeholder in inputs_data:
            edit = UnderlineEdit(placeholder, central_widget)
            layout.addWidget(edit)

        info_label = QLabel(
            "✓ 浮动标签不再被裁剪\n"
            "✓ 光标更贴近底部指示线\n"
            "✓ 整体更符合 Material Design 视觉规范",
            self
        )
        info_label.setStyleSheet("color: #a6e3a1; font-size: 12px; padding: 10px;")
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)


def main():
    app = QApplication(sys.argv)
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()