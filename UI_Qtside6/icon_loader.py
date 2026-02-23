# UI_Qtside6/icon_loader.py
import os
from PySide6.QtGui import QIcon, QPixmap

class IconLoader:
    """图标加载器"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_icons()
        return cls._instance

    def _init_icons(self):
        """初始化图标路径"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.dirname(current_dir)
        self.icon_dir = os.path.join(self.project_root, "asset", "icon")

        self.icon_files = {
            'math': 'abacus.svg',
            'calculate': 'calculate.png',
            'calculator': 'calculator.svg',
            'calculator_off': 'abacus-off.svg',
            'aquarius': 'aquarius.png',
            'tower': 'tower.svg'
        }

    def get_icon(self, icon_name, size=None):
        """获取图标"""
        if icon_name not in self.icon_files:
            return QIcon()

        icon_path = os.path.join(self.icon_dir, self.icon_files[icon_name])

        if not os.path.exists(icon_path):
            print(f"警告: 图标文件不存在 - {icon_path}")
            return QIcon()

        icon = QIcon(icon_path)

        if size:
            pixmap = icon.pixmap(size, size)
            return QIcon(pixmap)

        return icon

    def get_pixmap(self, icon_name, width=None, height=None):
        """获取QPixmap"""
        if icon_name not in self.icon_files:
            return QPixmap()

        icon_path = os.path.join(self.icon_dir, self.icon_files[icon_name])

        if not os.path.exists(icon_path):
            return QPixmap()

        pixmap = QPixmap(icon_path)

        if width and height:
            pixmap = pixmap.scaled(width, height)
        elif width:
            pixmap = pixmap.scaledToWidth(width)
        elif height:
            pixmap = pixmap.scaledToHeight(height)

        return pixmap

    def list_available_icons(self):
        """列出所有可用图标"""
        available = []
        for name, filename in self.icon_files.items():
            path = os.path.join(self.icon_dir, filename)
            if os.path.exists(path):
                available.append((name, filename))
        return available

icon_loader = IconLoader()