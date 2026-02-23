from PySide6.QtWidgets import (
    QWidget, QPushButton,QVBoxLayout, QLabel
)
from PySide6.QtCore import (
    Qt, QPropertyAnimation, QRect, QEasingCurve, QPoint, QAbstractAnimation
)
from PySide6.QtGui import QFont, QPainter, QLinearGradient, QColor, QPen
from PySide6.QtWidgets import QGraphicsOpacityEffect

class ResultCard(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.setFixedHeight(450)
        self.full_width = 280

        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)

        self.setStyleSheet("""
            background: #1e1e2e;
            border: 1px solid #3a3a3a;
            border-radius: 10px;
            box-shadow: 6px 6px 20px rgba(0,0,0,0.4), 
                       inset 0 -1px 3px rgba(0,0,0,0.3);
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        title = GradientLabel("预测数据")
        title.setFont(QFont("Microsoft YaHei", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setFixedHeight(50)
        layout.addWidget(title)

        self.content_label = QLabel()
        self.content_label.setFixedHeight(130)
        self.content_label.setWordWrap(True)
        self.content_label.setTextFormat(Qt.RichText)

        text1 = (
            '<span style="color:#4CAF50; font-weight:bold; font-size:24px;">DCR: 16.326 mΩ</span>'
            '<br><br>'

            '<span style="color:#4CAF50; font-weight:normal; font-size:12px;">DCR±5%: 15.509 ~ 17.142 mΩ</span>'
            '<br>'

            '<span style="color:#4CAF50; font-weight:normal; font-size:12px;">SK料号: SPT0530-R27M-BA</span>'
            '<br>'
        )
        self.content_label.setAlignment(Qt.AlignCenter)
        self.content_label.setText(text1)
        self.content_label.setStyleSheet("""color: #e0e0e0;""")
        layout.addWidget(self.content_label)
        self.content_label_2 = QLabel()
        self.content_label_2.setFixedHeight(130)
        self.content_label_2.setWordWrap(True)
        self.content_label_2.setTextFormat(Qt.RichText)

        text2 = (
            '<span style="color:#4CAF50; font-weight:bold; font-size:18px;">预估线圈规格: 0.10*1.00*2.20*1.75 T </span>'
            '<br><br>'
            
            '<span style="color:#4CAF50; font-weight:normal; font-size:12px;">DCR: 16.326 mΩ</span>'
            '<br>'
            
            '<span style="color:#4CAF50; font-weight:normal; font-size:12px;">SK料号: SPT0516-R68M-BA</span>'
            '<br>'
        )
        self.content_label_2.setAlignment(Qt.AlignCenter)
        self.content_label_2.setText(text2)
        self.content_label_2.setStyleSheet("""color: #e0e0e0;""")
        layout.addWidget(self.content_label_2)
        clear_btn = QPushButton("隐藏")
        clear_btn.setFixedHeight(45)
        clear_btn.setStyleSheet("""
                    QPushButton {
                        background: #45475a;
                        color: #cdd6f4;
                        border: none;
                        border-radius: 6px;
                        padding: 8px 12px;
                        font-size: 14px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
                    }
                    QPushButton:hover {
                        background: #34495e;
                        color: #bdc3c7;
                        box-shadow: 0 3px 6px rgba(0,0,0,0.4);
                    }
                    QPushButton:pressed {
                        background: #1a252f;
                        color: #ecf0f1;
                    }
                """)
        clear_btn.clicked.connect(self.hide_card)
        layout.addWidget(clear_btn)

        self.hide()
        self.anim_geo = None
        self.anim_opacity = None


    def _get_target_rect(self):
        """计算卡片应该在的位置（相对于主窗口右侧居中）"""
        parent_geo = self.main_window.geometry()
        parent_global = self.main_window.mapToGlobal(QPoint(0, 0))
        card_left = parent_global.x() + parent_geo.width()
        card_top = parent_global.y() + (parent_geo.height() - self.height()) // 2
        return QRect(card_left, card_top, self.full_width, self.height())

    def show_card(self):
        if (self.anim_geo and self.anim_geo.state() == QAbstractAnimation.Running) or \
                (self.anim_opacity and self.anim_opacity.state() == QAbstractAnimation.Running):
            return

        target = self._get_target_rect()
        start_rect = QRect(target.left(), target.top(), 2, target.height())

        self.setGeometry(start_rect)
        self.opacity_effect.setOpacity(0.0)
        self.show()

        self.anim_geo = QPropertyAnimation(self, b"geometry")
        self.anim_geo.setDuration(250)
        self.anim_geo.setEasingCurve(QEasingCurve.OutCubic)
        self.anim_geo.setStartValue(start_rect)
        self.anim_geo.setEndValue(target)

        self.anim_opacity = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim_opacity.setDuration(200)
        self.anim_opacity.setStartValue(0.0)
        self.anim_opacity.setEndValue(1.0)
        self.anim_opacity.setEasingCurve(QEasingCurve.OutCubic)

        self.anim_geo.start()
        self.anim_opacity.start()

    def hide_card(self):
        if not self.isVisible():
            return
        if (self.anim_geo and self.anim_geo.state() == QAbstractAnimation.Running) or \
                (self.anim_opacity and self.anim_opacity.state() == QAbstractAnimation.Running):
            return

        current = self.geometry()
        end_rect = QRect(current.x(), current.y(), 2, current.height())

        self.anim_geo = QPropertyAnimation(self, b"geometry")
        self.anim_geo.setDuration(200)
        self.anim_geo.setEasingCurve(QEasingCurve.InCubic)
        self.anim_geo.setStartValue(current)
        self.anim_geo.setEndValue(end_rect)

        self.anim_opacity = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim_opacity.setDuration(150)
        self.anim_opacity.setStartValue(1.0)
        self.anim_opacity.setEndValue(0.0)
        self.anim_opacity.setEasingCurve(QEasingCurve.InCubic)

        self.anim_opacity.finished.connect(self._on_hide)
        self.anim_geo.start()
        self.anim_opacity.start()

    def _on_hide(self):
        self.hide()
        self.anim_geo = None
        self.anim_opacity = None
        self.content_label.setText("")
        self.opacity_effect.setOpacity(1.0)

    def set_content(self, text: str):
        self.content_label.setText(text)

    def update_position(self):
        """仅更新位置，不动画（用于主窗口移动时同步）"""
        if not self.isVisible():
            return
        if (self.anim_geo and self.anim_geo.state() == QAbstractAnimation.Running) or \
                (self.anim_opacity and self.anim_opacity.state() == QAbstractAnimation.Running):
            return

        target = self._get_target_rect()
        current_width = self.width()
        new_rect = QRect(target.left(), target.top(), current_width, target.height())
        self.setGeometry(new_rect)

    def is_animating(self):
        return (self.anim_geo and self.anim_geo.state() == QAbstractAnimation.Running) or \
               (self.anim_opacity and self.anim_opacity.state() == QAbstractAnimation.Running)

class GradientLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._text = text
        self.setFont(QFont("Microsoft YaHei", 18, QFont.Bold))
        self.setFixedHeight(50)
        self.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

    def setText(self, text):
        self._text = text
        super().setText("")

    def paintEvent(self, event):
        if not self._text:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing | QPainter.TextAntialiasing)

        gradient = QLinearGradient(0, 0, self.width(), 0)
        gradient.setColorAt(0.0, QColor("#4CAF50"))
        gradient.setColorAt(1.0, QColor("#2196F3"))

        pen = QPen()
        pen.setBrush(gradient)
        painter.setPen(pen)

        painter.setFont(self.font())
        painter.drawText(self.rect(), Qt.AlignCenter, self._text)