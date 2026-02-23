import math
import sys
import os

from PySide6.QtCore import QRectF, QTimer, QDateTime
from PySide6.QtGui import Qt, QLinearGradient, QColor, QPainterPath, QFont, QPainter, QIcon
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QSizePolicy, \
    QHBoxLayout, QPushButton

from source import (
    extract_product_size_from_part_number,
    parse_coil_spec,
    calculate_dcr_with_inferred_flange,
    reverse_engineer_wire_thickness,
    parse_inductance_code,
    Reverse_coil_turns
)

from FloatingBotton import FloatingLabel_Btn
from UnderlineEdit import UnderlineEdit
from ResultCard import ResultCard
from icon_loader import icon_loader
from floating_preset_label import FloatingPresetLabel

current_dir = os.path.dirname(__file__)
icon_path = os.path.join(current_dir, "..", "asset", "icon", "aquarius.png")
icon_path = os.path.abspath(icon_path)


def create_title_widgets(parent):
    """返回 (主标题, 副标题) 两个 QLabel，不创建布局"""


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

class SmoothBlueCyanGlowTitle(QWidget):
    def __init__(self, text="XIAO_LAN", font_size=24,parent=None):
        super().__init__(parent)
        self.text = text
        self.setFixedSize(270, 70)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMaximumHeight(100)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

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

        color_blue = (35, 100, 255)
        color_cyan = (0, 180, 180)

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
        font = QFont("Microsoft YaHei", 18, QFont.Bold)
        painter.setFont(font)
        painter.drawText(text_rect, Qt.AlignCenter, self.text)

class XIAO_LAN_Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(icon_path))
        self.result_card = ResultCard(self)
        self.initUI()
        self.apply_icons()
        self.create_right_floating_labels()

    def initUI(self):
        self.setWindowTitle("DCR 计算器")
        self.setFixedSize(300, 450)
        self.setStyleSheet("background-color: #1e1e2e; color: #cdd6f4;")

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15,20,15,20)
        main_layout.setSpacing(20)

        title_widget = QWidget()
        title_layout = QVBoxLayout(title_widget)
        title_layout.setContentsMargins(0, 0, 0, 0)

        self.title_label = SmoothBlueCyanGlowTitle("DCR计算器")
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
        """创建预设按钮"""
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
        """应用预设规格"""
        if hasattr(self, 'spec_edit'):
            self.spec_edit.setText(spec)
            self.show_preset_applied_effect()

    def apply_icons(self):
        """应用所有图标"""
        available = icon_loader.list_available_icons()
        print("可用图标:")
        for name, filename in available:
            print(f"  {name}: {filename}")
        if hasattr(self, 'btn_calculate'):
            self.btn_calculate.setIcon(icon_loader.get_icon('math', 32))
        if hasattr(self, 'btn_reset'):
            self.btn_reset.setIcon(icon_loader.get_icon('calculator_off', 24))
        if hasattr(self, 'action_save'):
            self.action_save.setIcon(icon_loader.get_icon('calculate'))
        if hasattr(self, 'logo_label'):
            pixmap = icon_loader.get_pixmap('aquarius', 100, 100)
            self.logo_label.setPixmap(pixmap)

    def on_calculate(self):
        try:
            part_number, spec_str = self.get_and_validate_inputs()
            try:
                target_number, target_dcr = self.get_target_inputs()
                has_target = bool(target_number and target_dcr is not None)
            except ValueError as target_error:
                has_target = False
                text2 = self.build_input_error_display(target_error)
                self.display_partial_results(text1=None, text2=text2, show_card=True)
                return
            result_data_1 = self.perform_calculation(part_number, spec_str)
            text1 = self.build_primary_display(result_data_1)

            if has_target:
                try:
                    result_data_2 = self.perform_calculation_card2(
                        part_number, spec_str, target_number, target_dcr
                    )
                    text2 = self.build_primary_display_card2(result_data_2)
                except Exception as e:
                    text2 = self.build_target_calculation_error(str(e))
            else:
                text2 = self.build_no_target_input_display()
            self.display_partial_results(text1, text2, show_card=True)

        except Exception as ex:
            error_html = self.build_error_display(str(ex))
            self.display_partial_results(error_html, "", show_card=True)

    def get_and_validate_inputs(self):
        """获取并验证输入"""
        part_number = self.part_edit.text().strip()
        spec_str = self.spec_edit.text().strip()

        if not part_number or not spec_str:
            raise ValueError("参考料号和线圈规格不对")

        return part_number, spec_str

    def get_target_inputs(self):
        """获取目标输入（可选）"""
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

    def perform_calculation(self, part_number, spec_str):
        """执行计算，返回所有数据"""
        try:
            product_size = extract_product_size_from_part_number(part_number)
            coil = parse_coil_spec(spec_str)

            dcr_nom, dcr_min, dcr_max = calculate_dcr_with_inferred_flange(coil, product_size)

            dcr_nom_m = dcr_nom * 1000
            dcr_min_m = dcr_min * 1000
            dcr_max_m = dcr_max * 1000

            return {
                'part_number': part_number,
                'spec_str': spec_str,
                'product_size': product_size,
                'coil': coil,
                'wire_thickness': coil.wire_thickness_mm,  #  线厚
                'wire_width': coil.wire_width_mm,  #  线宽
                'inner_diameter': coil.inner_diameter_mm,  #  内径
                'turns': coil.turns,  #  圈数
                'dcr_nom_m': dcr_nom_m,
                'dcr_min_m': dcr_min_m,
                'dcr_max_m': dcr_max_m,
                'timestamp': QDateTime.currentDateTime()
            }
        except Exception as e:
            raise ValueError(f"计算过程出错: {str(e)}")

    def perform_calculation_card2(self, part_number, spec_str, target_number, target_dcr):
        """执行计算，返回所有数据"""
        try:
            product_size = extract_product_size_from_part_number(part_number)
            product_size1 = extract_product_size_from_part_number(target_number)

            def extract_inductance_code(full_part_number):
                """从零件号中提取电感编码部分"""
                parts = full_part_number.split('-')

                if len(parts) == 1:
                    return parts[0]
                elif len(parts) == 2:
                    return parts[1]
                elif len(parts) >= 3:
                    for part in parts[1:]:
                        if any(keyword in part.upper() for keyword in ['R', 'L', 'UH', 'NH', 'MH']):
                            return part
                    return parts[-2]
                return ""

            inductance_part1 = extract_inductance_code(part_number)
            inductance_part2 = extract_inductance_code(target_number)

            result_inductance1 = parse_inductance_code(inductance_part1)
            result_inductance2 = parse_inductance_code(inductance_part2)

            cnp_ent = result_inductance2['value_uh'], result_inductance1['value_uh']

            coil = parse_coil_spec(spec_str)
            n2e = Reverse_coil_turns(coil, cnp_ent)
            n3e, approximate_dcr = reverse_engineer_wire_thickness(
                coil, product_size1, target_dcr, n2e
            )
            # print(f"调试信息:")
            # print(f"  目标DCR: {target_dcr}")
            # print(f"  计算出的近似DCR: {approximate_dcr}")
            # print(f"  差值: {abs(float(approximate_dcr) - float(target_dcr))}")
            return {
                'target_number': target_number,
                'product_size': product_size,
                'coil': coil,
                'wire_thickness': n3e,
                'wire_width': coil.wire_width_mm,
                'inner_diameter': coil.inner_diameter_mm,
                'approximate_dcr': approximate_dcr,
                'new_turns': n2e,
                'timestamp': QDateTime.currentDateTime()
            }
        except Exception as e:
            raise ValueError(f"计算过程出错: {str(e)}")

    def build_primary_display(self, data):
        """构建主要显示内容（DCR结果）"""
        return (
            f'<div style="text-align: center;">'
            f'<span style="color:#4CAF50; font-weight:bold; font-size:24px;">'
            f'DCR(P2): {data["dcr_nom_m"]:.3f} mΩ</span><br><br>'

            f'<span style="color:#4CAF50; font-size:12px;">DCR±5%:</span> '
            f'<span style="color:#e0e0e0; font-size:12px;">'
            f'{data["dcr_min_m"]:.3f} ~ {data["dcr_max_m"]:.3f} mΩ</span><br>'

            f'<span style="color:#4CAF50; font-size:12px;">参考料号:</span> '
            f'<span style="color:#e0e0e0; font-size:12px;">{data["part_number"]}</span>'
            f'</div>'
        )

    def build_primary_display_card2(self, data2):
        """构建第二个显示内容（预测结果）"""
        if data2.get('wire_thickness'):
            return (
                f'<div style="text-align: center;">'
                f'<span style="color:#4CAF50; font-weight:bold; font-size:18px;">'
                f'预估线圈规格: {data2["wire_thickness"]:.2f}*{data2["wire_width"]:.2f}*'
                f'{data2["inner_diameter"]:.2f}*{data2["new_turns"]:.2f}T</span><br><br>'

                f'<span style="color:#4CAF50; font-size:12px;">目标料号:</span> '
                f'<span style="color:#e0e0e0; font-size:12px;">{data2["target_number"]}</span><br>'

                f'<span style="color:#4CAF50; font-size:12px;">目标DCR:</span> '
                f'<span style="color:#e0e0e0; font-size:12px;">{data2.get("approximate_dcr"):.2f} mΩ</span>'
                f'</div>'
            )
        else:
            return (
                f'<div style="text-align: center;">'
                f'<span style="color:#4CAF50; font-weight:bold; font-size:18px;">'
                f'预测线圈信息</span><br><br>'

                f'<span style="color:#4CAF50; font-size:12px;">目标料号:</span> '
                f'<span style="color:#e0e0e0; font-size:12px;">{data2.get("target_number", "N/A")}</span><br>'

                f'<span style="color:#4CAF50; font-size:12px;">新圈数:</span> '
                f'<span style="color:#e0e0e0; font-size:12px;">{data2.get("new_turns", "N/A"):.2f}T</span>'
                f'</div>'
            )

    def display_partial_results(self, text1=None, text2=None, show_card=True):
        """分别更新两个内容区域"""
        if text1 is not None:
            self.result_card.content_label.clear()
            self.result_card.content_label.setText(text1)

        if text2 is not None:
            self.result_card.content_label_2.clear()
            self.result_card.content_label_2.setText(text2)

        if show_card:
            self.result_card.show_card()

    def display_results(self, text1, text2=None):
        """兼容旧版本的显示方法"""
        self.display_partial_results(text1, text2, show_card=True)

    def build_no_target_input_display(self):
        """构建无目标输入的显示内容"""
        return '''
            <div style="text-align: center; padding: 15px;">
                <span style="color:#B0BEC5; font-size: 14px;">
                    ⏳ 等待目标输入
                </span><br>
                <span style="color:#757575; font-size: 12px;">
                    请输入目标料号和目标DCR进行预测
                </span>
            </div>
        '''

    def build_input_error_display(self, error_msg):
        """构建输入错误的显示内容"""
        return f'''
            <div style="padding: 10px;">
                <span style="color:#FF9800; font-weight:bold; font-size:12px;">
                    ⚠️ 目标输入错误
                </span><br>
                <span style="color:#FFCC80; font-size:11px;">
                    {error_msg}
                </span>
            </div>
        '''

    def build_target_calculation_error(self, error_msg):
        """构建目标计算错误的显示内容"""
        return f'''
            <div style="padding: 10px;">
                <span style="color:#FF5252; font-weight:bold; font-size:12px;">
                    ❌ 预测失败
                </span><br>
                <span style="color:#FF8A80; font-size:11px;">
                    {error_msg}
                </span>
            </div>
        '''

    def build_error_display(self, error_msg):
        """构建主要错误显示"""
        return f'''
            <div style="padding: 20px; text-align: center;">
                <span style="color:#FF5252; font-weight:bold; font-size:12px;">
                    ❌ 计算失败
                </span><br><br>
                <span style="color:#FF8A80; font-size:11px;">
                    {error_msg}
                </span>
            </div>
        '''
    def display_error(self, error_msg):
        """显示错误信息"""
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
        """创建横向输入框区域"""
        container = QWidget(parent)
        h_layout = QHBoxLayout(container)
        h_layout.setSpacing(20)
        h_layout.setContentsMargins(0, 0, 0, 0)

        self.target_part_field  = UnderlineEdit("目标料号", container)
        self.target_DCR_field = UnderlineEdit("DCR(TYP)mΩ", container)

        for edit in (self.target_part_field, self.target_DCR_field):
            edit.setMinimumSize(50, 20)

        self.target_part_field.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.target_DCR_field.setFixedWidth(100)

        h_layout.addWidget(self.target_part_field)
        h_layout.addWidget(self.target_DCR_field)

        return container

    def create_button_section(self):
        """创建按钮区域"""
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
        """清除所有输入框"""
        self.part_edit.clear()
        self.spec_edit.clear()
        self.target_part_field.clear()
        self.target_DCR_field.clear()

    def moveEvent(self, e):
        """窗口移动时更新 ResultCard 位置"""
        super().moveEvent(e)
        if hasattr(self, 'result_card') and self.result_card and self.result_card.isVisible():
            self.result_card.update_position()

    def resizeEvent(self, e):
        """窗口大小变化时更新 ResultCard 位置"""
        super().resizeEvent(e)
        if hasattr(self, 'result_card') and self.result_card and self.result_card.isVisible():
            self.result_card.update_position()

    def closeEvent(self, e):
        """关闭窗口时同时关闭 ResultCard"""
        if hasattr(self, 'result_card') and self.result_card:
            self.result_card.close()
        e.accept()

    def create_right_floating_labels(self):
        labels_data = [
            ("🔧 04系列", "SPT0420-2R2M-BA", "0.20*0.80*1.60*3.75", "#89dceb"),
            ("📱 05系列", "SPT0530-R33M-BA", "0.35*1.00*2.20*2.75", "#cba6f7"),
            ("⚡ 06系列", "SPT0620-2R2M-BA", "0.20*1.20*2.70*3.75", "#f38ba8"),
        ]
        created_labels = []

        title_label = QLabel("快速规格预设", self)  # ← parent 是 self
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
        """当点击浮动预设标签时，自动填充输入框"""
        if hasattr(self, 'part_edit') and hasattr(self, 'spec_edit'):
            self.part_edit.setText(model)
            self.spec_edit.setText(spec)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = XIAO_LAN_Window()
    window.show()
    sys.exit(app.exec())