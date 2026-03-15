import sys
import os

_current_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(_current_dir)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QSizePolicy, QHBoxLayout, QPushButton

from source.calculator_service import (
    perform_dcr_calculation,
    perform_target_calculation,
    format_primary_display,
    format_target_display,
    format_error_display,
    format_no_target_display,
    format_input_error_display,
    format_target_calculation_error,
)
from UI_Qtside6.shining_glow_title import SmoothBlueCyanGlowTitle
from UI_Qtside6.FloatingBotton import FloatingLabel_Btn
from UI_Qtside6.UnderlineEdit import UnderlineEdit
from UI_Qtside6.ResultCard import ResultCard
from UI_Qtside6.floating_preset_label import FloatingPresetLabel

current_dir = os.path.dirname(__file__)
icon_path = os.path.join(current_dir, "..", "asset", "icon", "tower.svg")
icon_path = os.path.abspath(icon_path)


def create_title_widgets(parent):
    f_biao_ti = QLabel("　　通过参考料号/线圈推算需求料号和目标DCR推荐线圈规格。", parent)
    f_biao_ti.setWordWrap(True)
    f_biao_ti.setAlignment(Qt.AlignTop)
    f_biao_ti.setFixedHeight(50)
    f_biao_ti.setStyleSheet("""QLabel {
            font-size: 12px;
            font-weight: normal;
            color: #cdd6f4;
            margin: 5px;
            padding: 0px;
            background-color: #1e1e2e;
            border: 0px;
            }""")
    return f_biao_ti


class XIAO_LAN_Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(icon_path))
        self.result_card = ResultCard(self)
        self.initUI()
        self.create_right_floating_labels()

    def initUI(self):
        self.setWindowTitle("DCR 计算器")
        self.setFixedSize(300, 450)
        self.setStyleSheet("background-color: #1e1e2e; color: #cdd6f4;")

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 20, 15, 20)
        main_layout.setSpacing(20)

        title_widget = QWidget()
        title_layout = QVBoxLayout(title_widget)
        title_layout.setContentsMargins(0, 0, 0, 0)

        self.title_label = SmoothBlueCyanGlowTitle("DCR计算器", font_size=18, width=270, height=70)
        title_layout.addWidget(self.title_label, alignment=Qt.AlignCenter)

        subtitle_label = create_title_widgets(self)
        title_layout.addWidget(subtitle_label)
        main_layout.addWidget(title_widget)

        self.part_edit = UnderlineEdit("参考料号", self)
        self.spec_edit = UnderlineEdit("线圈规格", self)
        self.part_edit.setFixedWidth(150)
        self.spec_edit.setFixedWidth(150)
        main_layout.addWidget(self.part_edit)
        main_layout.addWidget(self.spec_edit)

        horizontal_section = self.create_horizontal_inputs(self)
        main_layout.addWidget(horizontal_section)

        btn_widget = self.create_button_section()
        main_layout.addWidget(btn_widget)

        self.setLayout(main_layout)

    def create_preset_button(self, name, spec, color):
        btn = QPushButton(name)
        btn.setToolTip(f"点击应用:\n{spec}")

        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #313244;
                color: {color};
                border: 1px solid {color}40;
                border-radius: 5px;
                padding: 8px 5px;
                font-size: 12px;
                font-weight: bold;
                text-align: left;
                padding-left: 10px;
                min-height: 35px;
            }}
            QPushButton:hover {{
                background-color: {color}15;
                border: 1px solid {color};
            }}
            QPushButton:pressed {{
                background-color: {color}30;
            }}
        """)

        btn.clicked.connect(lambda checked, s=spec: self.apply_preset_spec(s))

        return btn

    def apply_preset_spec(self, spec):
        if hasattr(self, "spec_edit"):
            self.spec_edit.setText(spec)
            self._show_preset_applied_effect()

    def _show_preset_applied_effect(self):
        pass

    def on_calculate(self):
        try:
            part_number, spec_str = self.get_and_validate_inputs()
            try:
                target_number, target_dcr = self.get_target_inputs()
                has_target = bool(target_number and target_dcr is not None)
            except ValueError as target_error:
                has_target = False
                text2 = format_input_error_display(str(target_error))
                self.display_partial_results(text1=None, text2=text2, show_card=True)
                return

            result_data_1 = perform_dcr_calculation(part_number, spec_str)
            text1 = format_primary_display(result_data_1)

            if has_target:
                try:
                    result_data_2 = perform_target_calculation(
                        part_number, spec_str, target_number, target_dcr
                    )
                    text2 = format_target_display(result_data_2)
                except Exception as e:
                    text2 = format_target_calculation_error(str(e))
            else:
                text2 = format_no_target_display()
            self.display_partial_results(text1, text2, show_card=True)

        except Exception as ex:
            error_html = format_error_display(str(ex))
            self.display_partial_results(error_html, "", show_card=True)

    def get_and_validate_inputs(self):
        part_number = self.part_edit.text().strip()
        spec_str = self.spec_edit.text().strip()

        if not part_number or not spec_str:
            raise ValueError("参考料号和线圈规格不对")

        return part_number, spec_str

    def get_target_inputs(self):
        target_number = self.target_part_field.text().strip() if hasattr(self, 'target_part_field') else ""
        target_dcr_str = self.target_DCR_field.text().strip() if hasattr(self, 'target_DCR_field') else ""

        target_dcr = None
        if target_dcr_str:
            try:
                target_dcr = float(target_dcr_str)
                if target_dcr <= 0:
                    raise ValueError("目标DCR必须大于0")
            except ValueError:
                raise ValueError(f"目标DCR格式错误: '{target_dcr_str}'只支持数字")

        return target_number, target_dcr

    def display_partial_results(self, text1=None, text2=None, show_card=True):
        if text1 is not None:
            self.result_card.content_label.clear()
            self.result_card.content_label.setText(text1)

        if text2 is not None:
            self.result_card.content_label_2.clear()
            self.result_card.content_label_2.setText(text2)

        if show_card:
            self.result_card.show_card()

    def display_results(self, text1, text2=None):
        self.display_partial_results(text1, text2, show_card=True)

    def display_error(self, error_msg):
        error_html = (
            f'<div style="margin-bottom: 15px;">'
            f'<span style="color:#FF5252; font-weight:bold; font-size:12px; '
            f'background-color: rgba(255, 82, 82, 0.1); padding: 3px 10px; border-radius: 3px;">'
            f'❌ 错误区</span>'
            f'</div>'
            f'<span style="color:#FF5252; font-size:16px;">计算失败</span><br><br>'
            f'<span style="color:#FF8A80; font-size:14px;">{error_msg}</span><br><br>'
            f'<span style="color:#B0BEC5; font-size:12px;">请检查输入后重试</span>'
        )

        self.result_card.content_label.clear()
        self.result_card.content_label.setText(error_html)
        self.result_card.show_card()

    def create_horizontal_inputs(self, parent):
        container = QWidget(parent)
        h_layout = QHBoxLayout(container)
        h_layout.setSpacing(20)
        h_layout.setContentsMargins(0, 0, 0, 0)

        self.target_part_field = UnderlineEdit("目标料号", container)
        self.target_DCR_field = UnderlineEdit("DCR(TYP)mΩ", container)

        for edit in (self.target_part_field, self.target_DCR_field):
            edit.setMinimumSize(50, 20)

        self.target_part_field.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.target_DCR_field.setFixedWidth(100)

        h_layout.addWidget(self.target_part_field)
        h_layout.addWidget(self.target_DCR_field)

        return container

    def create_button_section(self):
        button_widget = QWidget()
        layout = QHBoxLayout(button_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 10, 20, 10)

        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        icon_dir = os.path.join(project_root, "asset", "icon")

        calculate_icon = os.path.join(icon_dir, "abacus.svg")
        clear_icon = os.path.join(icon_dir, "abacus-off.svg")

        btn_check = FloatingLabel_Btn(
            "计算",
            icon_path=calculate_icon if os.path.exists(calculate_icon) else None
        )
        btn_check.clicked.connect(self.on_calculate)

        btn_cancel = FloatingLabel_Btn(
            "清除",
            icon_path=clear_icon if os.path.exists(clear_icon) else None
        )
        btn_cancel.clicked.connect(self.clear_inputs)

        for btn in [btn_check, btn_cancel]:
            btn.setMinimumSize(100, 30)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout.addWidget(btn_check)
        layout.addWidget(btn_cancel)

        return button_widget

    def clear_inputs(self):
        self.part_edit.clear()
        self.spec_edit.clear()
        self.target_part_field.clear()
        self.target_DCR_field.clear()

    def moveEvent(self, e):
        super().moveEvent(e)
        if hasattr(self, 'result_card') and self.result_card and self.result_card.isVisible():
            self.result_card.update_position()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if hasattr(self, 'result_card') and self.result_card and self.result_card.isVisible():
            self.result_card.update_position()

    def closeEvent(self, e):
        if hasattr(self, 'result_card') and self.result_card:
            self.result_card.close()
        e.accept()

    def hideEvent(self, e):
        super().hideEvent(e)
        if hasattr(self, 'result_card') and self.result_card:
            self._result_card_was_visible = self.result_card.isVisible()
            self.result_card.hide()

    def showEvent(self, e):
        super().showEvent(e)
        if hasattr(self, 'result_card') and self.result_card:
            if getattr(self, '_result_card_was_visible', False):
                self.result_card.show_card()

    def changeEvent(self, e):
        super().changeEvent(e)
        if hasattr(self, 'result_card') and self.result_card and self.result_card.isVisible():
            if self.isActiveWindow():
                self.result_card.raise_()
                self.raise_()

    def create_right_floating_labels(self):
        labels_data = [
            ("🔧 04系列", "SPT0420-2R2M-BA", "0.20*0.80*1.60*3.75", "#89dceb"),
            ("📱 05系列", "SPT0530-R33M-BA", "0.35*1.00*2.20*2.75", "#cba6f7"),
            ("⚡ 06系列", "SPT0620-2R2M-BA", "0.20*1.20*2.70*3.75", "#f38ba8"),
        ]
        created_labels = []

        title_label = QLabel("快速规格预设", self)
        title_label.setStyleSheet("""
            color: #89dceb;
            font-size: 12px;
            font-weight: bold;
            background: transparent;
            border: none;
        """)
        title_label.setAttribute(Qt.WA_TransparentForMouseEvents)
        title_label.show()

        for name, model, spec, color in labels_data:
            label = FloatingPresetLabel(name, model, spec, color, self)
            label.clicked.connect(self.on_preset_clicked)
            created_labels.append(label)
            label.show()

        def update_all_label_positions():
            tw = title_label.sizeHint().width()
            x_title = self.width() - tw - 32
            y_title = 140
            title_label.move(x_title, y_title)

            for i, label in enumerate(created_labels):
                lw = label.sizeHint().width()
                x = self.width() - lw - 27
                y = 180 + i * 35
                label.set_position(x, y)

        update_all_label_positions()

        self._floating_title = title_label
        self._floating_labels = created_labels

        original_resize = self.resizeEvent

        def on_resize(e):
            original_resize(e)
            update_all_label_positions()

        self.resizeEvent = on_resize

    def on_preset_clicked(self, model: str, spec: str):
        if hasattr(self, 'part_edit') and hasattr(self, 'spec_edit'):
            self.part_edit.setText(model)
            self.spec_edit.setText(spec)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = XIAO_LAN_Window()
    window.show()
    sys.exit(app.exec())
