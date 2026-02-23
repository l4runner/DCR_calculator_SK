from PySide6.QtWidgets import QLabel, QHBoxLayout, QFrame
from PySide6.QtCore import Qt, QPropertyAnimation, QPoint, QEasingCurve, Signal, QTimer
import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel


class FloatingPresetLabel(QLabel):
    """固定在右侧的浮动标签"""
    clicked = Signal(str,str)

    def __init__(self, text, model, spec, color="#89dceb", parent=None):
        super().__init__(parent)
        self.text = text
        self.model = model      # 型号，如 "SPT0530-R33M-BA"
        self.spec = spec        # 规格，如 "0.35*1.00*2.20*2.75T"
        self.color = color
        self.is_hovered = False
        self.float_distance = 2
        self.original_pos = None
        self.setFixedWidth(80)
        self.init_ui()
        QTimer.singleShot(100, self.set_fixed_original_pos)

    def init_ui(self):
        """初始化UI"""
        self.setText(self.text)
        self.setAlignment(Qt.AlignCenter)

        self.setStyleSheet(f"""
            QLabel {{
                color: {self.color};
                font-size: 11px;
                font-weight: bold;
                padding: 2px 8px;
                border: 1px solid {self.color}40;
                border-radius: 10px;
                background-color: rgba(30, 30, 46, 0.8);
            }}
        """)

        self.setCursor(Qt.PointingHandCursor)
        self.pos_animation = QPropertyAnimation(self, b"pos")
        self.pos_animation.setDuration(150)
        self.pos_animation.setEasingCurve(QEasingCurve.OutCubic)

    def set_fixed_original_pos(self):
        """设置固定的原始位置（只调用一次）"""
        if self.original_pos is None:
            self.original_pos = self.pos()

    def set_position(self, x, y):
        """设置标签位置，并更新原始位置"""
        self.move(x, y)
        self.original_pos = QPoint(x, y)

    def enterEvent(self, event):
        if self.original_pos is None:
            self.original_pos = self.pos()
        self.is_hovered = True
        new_pos = self.original_pos - QPoint(0, self.float_distance)
        self.animate_position(new_pos)

        self.setStyleSheet(f"""
            QLabel {{
                color: {self.color};
                font-size: 11px;
                font-weight: bold;
                padding: 2px 8px;
                border: 1px solid {self.color};
                border-radius: 10px;
                background-color: rgba(30, 30, 46, 0.9);
            }}
        """)
        self.setToolTip(f"型号: {self.model}\n规格: {self.spec}")
        super().enterEvent(event)

    def leaveEvent(self, event):
        """鼠标离开事件"""
        self.is_hovered = False

        if self.original_pos is not None:
            self.animate_position(self.original_pos)

        self.setStyleSheet(f"""
            QLabel {{
                color: {self.color};
                font-size: 11px;
                font-weight: bold;
                padding: 2px 8px;
                border: 1px solid {self.color}40;
                border-radius: 10px;
                background-color: rgba(30, 30, 46, 0.8);
            }}
        """)

        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setStyleSheet(f"""
                QLabel {{
                    color: white;
                    font-size: 11px;
                    font-weight: bold;
                    padding: 2px 8px;
                    border: 1px solid {self.color};
                    border-radius: 10px;
                    background-color: {self.color};
                }}
            """)
            self.clicked.emit(self.model, self.spec)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.LeftButton:
            if self.is_hovered:
                self.setStyleSheet(f"""
                    QLabel {{
                        color: {self.color};
                        font-size: 11px;
                        font-weight: bold;
                        padding: 2px 8px;
                        border: 1px solid {self.color};
                        border-radius: 10px;
                        background-color: rgba(30, 30, 46, 0.9);
                    }}
                """)
            else:
                self.setStyleSheet(f"""
                    QLabel {{
                        color: {self.color};
                        font-size: 11px;
                        font-weight: bold;
                        padding: 2px 8px;
                        border: 1px solid {self.color}40;
                        border-radius: 10px;
                        background-color: rgba(30, 30, 46, 0.8);
                    }}
                """)
        super().mouseReleaseEvent(event)

    def animate_position(self, pos):
        """动画移动位置"""
        self.pos_animation.stop()
        self.pos_animation.setStartValue(self.pos())
        self.pos_animation.setEndValue(pos)
        self.pos_animation.start()

    def create_right_floating_presets(self):
        """创建靠右浮动的预设标签容器"""
        container = QWidget()
        container.setFixedHeight(45)

        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 10, 0, 5)

        layout.addStretch()

        floating_presets = [
            ("标准", "0.20*1.00*2.50*8T", "#89dceb"),
            ("高频", "0.15*0.80*1.80*5T", "#cba6f7"),
            ("大电流", "0.30*1.20*3.20*6T", "#f38ba8"),
        ]

        for name, spec, color in floating_presets:
            label = FloatingPresetLabel(name, spec, color)
            layout.addWidget(label)
            label.clicked.connect(lambda s=spec: self.apply_spec_from_label(s))

        return container


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle("右侧浮动预设标签")
    window.resize(300, 450)
    window.setStyleSheet("background-color: #1e1e2e; color: #cdd6f4;")
    main_layout = QVBoxLayout(window)
    main_layout.setContentsMargins(20, 20, 20, 20)
    main_layout.setSpacing(15)
    content_label = QLabel("主内容区域")
    content_label.setStyleSheet("""
        QLabel {
            background-color: #313244;
            border-radius: 8px;
            padding: 30px;
            border: 1px solid #585b70;
            min-height: 200px;
            font-size: 14px;
        }
    """)
    content_label.setAlignment(Qt.AlignCenter)
    main_layout.addWidget(content_label, 1)
    window.floating_labels = []

    def create_right_floating_labels():
        labels_data = [
            ("🔧 04系列", "SPT0420-2R2M-BA", "0.20*0.80*1.60*3.75T", "#89dceb"),
            ("📱 05系列", "SPT0530-R33M-BA", "0.35*1.00*2.20*2.75T", "#cba6f7"),
            ("⚡ 06系列", "SPT0620-2R2M-BA", "0.20*0.80*1.60*3.75T",  "#f38ba8"),
        ]
        created_labels = []
        title_label = QLabel("快速规格预设", window)
        title_label.setStyleSheet("color: #89dceb; font-size: 12px; font-weight: bold;background: transparent; border: none; ")
        title_label.setAttribute(Qt.WA_TransparentForMouseEvents)
        title_width = title_label.sizeHint().width()
        x_pos = window.width() - title_width - 55
        y_pos = 140
        title_label.move(x_pos, y_pos)

        for name, model,spec, color in labels_data:
            label = FloatingPresetLabel(name, model, spec, color, window)
            created_labels.append(label)

        def update_all_label_positions():
            for i, label in enumerate(created_labels):
                label_width = label.sizeHint().width()
                x_pos = window.width() - label_width - 50
                y_pos = 180 + i * 35
                label.set_position(x_pos, y_pos)

        update_all_label_positions()
        original_resize_event = window.resizeEvent

        def on_resize(e):
            original_resize_event(e)
            update_all_label_positions()

        window.resizeEvent = on_resize

    def resize_labels():
        """重新调整标签位置到右侧"""
        right_margin = 10
        vertical_spacing = 45
        start_y = 80

        for i, label in enumerate(window.floating_labels):
            label_width = label.width()
            x_pos = window.width() - label_width - right_margin
            y_pos = start_y + i * vertical_spacing

            label.move(x_pos, y_pos)

    original_resize = window.resizeEvent

    def custom_resize(event):
        original_resize(event)
        resize_labels()

    window.resizeEvent = custom_resize
    create_right_floating_labels()
    window.show()
    sys.exit(app.exec())