# UI_Qtside6/PopupAnimationDemo.py
import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QPushButton, QLabel, QGraphicsOpacityEffect
)
from PySide6.QtCore import (
    Qt, QRect, QPropertyAnimation, QParallelAnimationGroup,
    QEasingCurve
)


class AnimatedPopup(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(300, 180)
        self.setWindowTitle("动画弹窗")
        self.setWindowFlags(
            Qt.Window | Qt.WindowCloseButtonHint | Qt.WindowTitleHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 透明度效果
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)

        # 布局
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        label = QLabel("✨ 动画弹出成功！")
        label.setStyleSheet("font-size: 16px; color: white;")
        layout.addWidget(label)
        self.setLayout(layout)

        # 设置初始透明
        self.opacity_effect.setOpacity(0.0)

        # 动画组
        self.anim_group = QParallelAnimationGroup()

        # 位置动画
        self.pos_anim = QPropertyAnimation(self, b"geometry")
        self.pos_anim.setDuration(400)
        self.pos_anim.setEasingCurve(QEasingCurve.OutCubic)

        # 透明度动画
        self.opacity_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.opacity_anim.setDuration(400)
        self.opacity_anim.setStartValue(0.0)
        self.opacity_anim.setEndValue(1.0)
        self.opacity_anim.setEasingCurve(QEasingCurve.OutCubic)

        self.anim_group.addAnimation(self.pos_anim)
        self.anim_group.addAnimation(self.opacity_anim)

        # 样式
        self.setStyleSheet("""
            AnimatedPopup {
                background-color: #1e1e2e;
                border-radius: 12px;
                border: 1px solid #585b70;
            }
        """)

    def show_with_animation(self):
        """调用此方法触发动画弹出"""
        parent = self.parent()
        if parent:
            parent_rect = parent.geometry()
        else:
            screen = QApplication.primaryScreen()
            parent_rect = screen.geometry()

        # 目标位置（居中）
        target_x = parent_rect.x() + (parent_rect.width() - self.width()) // 2
        target_y = parent_rect.y() + (parent_rect.height() - self.height()) // 2
        target_rect = QRect(target_x, target_y, self.width(), self.height())

        # 起始位置：从底部外开始
        start_rect = QRect(target_x, parent_rect.bottom(), self.width(), self.height())

        self.setGeometry(start_rect)  # 先放到起始位置（透明，用户看不见）

        self.pos_anim.setStartValue(start_rect)
        self.pos_anim.setEndValue(target_rect)

        self.show()  # 显示窗口（但透明）
        self.anim_group.start()  # 启动动画


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("动画弹窗演示")
        self.setFixedSize(400, 300)
        self.popup = None

        central = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        label = QLabel("点击按钮查看动画弹窗")
        label.setStyleSheet("font-size: 14px; color: #cdd6f4;")
        btn = QPushButton("弹出动画窗口")
        btn.setFixedWidth(160)
        btn.clicked.connect(self.show_popup)

        layout.addWidget(label)
        layout.addWidget(btn)
        central.setLayout(layout)
        self.setCentralWidget(central)

        # 主窗口样式
        self.setStyleSheet("background-color: #11111b;")

    def show_popup(self):
        if self.popup is None:
            self.popup = AnimatedPopup(self)
            self.popup.destroyed.connect(lambda: setattr(self, 'popup', None))
        self.popup.show_with_animation()  # ← 关键：调用动画方法


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())