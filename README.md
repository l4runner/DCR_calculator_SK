# DCR Calculator（线圈直流电阻计算器）

<div align="left">

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PySide6](https://img.shields.io/badge/GUI-PySide6-green.svg)](https://doc.qt.io/qtforpython/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://makeapullrequest.com)

**一款专为电源/磁性元件工程师设计的桌面工具，用于快速推算线圈规格与理论DCR值**

 • [快速开始](#快速开始) • [使用指南](#使用指南) • [技术架构](#技术架构) • [项目结构](#项目结构)

</div>

---

## 项目简介

在电源设计和磁性元件选型过程中，工程师需要根据现有料号推算目标规格的DCR（直流电阻）值。传统方式依赖Excel表格或手工计算，既繁琐又容易出错。**DCR Calculator** 通过图形化界面封装电磁学经验公式，将这一过程简化为几秒内的精准计算。

### 痛点与解决方案

| 痛点 | 传统方式 | 本工具方案 |
|------|---------|-----------|
| 计算效率 | Excel公式维护复杂，查找困难 | 一键计算，结果即时呈现 |
| 出错概率 | 手工输入易错，公式引用易错 | 结构化输入，实时校验 |
| 专业门槛 | 需要记忆复杂公式 | 经验公式内置，专注设计本身 |
| 重复工作 | 同系列料号重复输入 | 预设模板，快速填充 |

### 核心优势

- **降低认知负担**：将电磁学经验公式封装于后台，工程师专注设计决策
- **现代化界面**：Material Design设计语言，Catppuccin Mocha深色主题
- **智能校验**：输入合法性实时验证，异常参数即时提示
- **系列预设**：内置多款系列标准模板
- **流畅交互**：基于Qt属性动画的平滑过渡效果

---

## 核心特性

### 双模式计算引擎

| 模式 | 适用场景 | 输入参数 | 输出结果 |
|------|---------|---------|---------|
| **正向计算** | 验证现有设计 | 参考料号 + 线圈规格 | DCR标称值、±5%容差范围 |
| **反向推演** | 新器件选型 | 目标料号 + 目标DCR | 预估线圈规格、推荐匝数、建议线径 |

### 核心算法

| 算法模块 | 功能描述 | 技术要点 |
|---------|---------|---------|
| DCR理论计算 | 基于线圈几何参数计算直流电阻 | 铜电阻率 ρ=1.68×10⁻⁸ Ω·m，温度系数校正 |
| 匝数反推 | 根据目标感值求解匝数 | 平方根关系 N₂ = N₁ × √(L₂/L₁) |
| 线径优化 | 二分查找最优线径 | 约束条件：压缩高度 ≤ 产品高度 |
| T-core几何 | 摆厚、中柱、引脚长度计算 | 经验系数与向上取整规则 |

### 界面交互

- **结果卡片**：右侧滑入式展示面板，双区域分别显示正向/反向计算结果
- **浮动标签输入**：Material Design风格，聚焦时标签上浮，底部指示线展开
- **快速预设**：右侧浮动标签，点击自动填充系列标准料号
- **按钮反馈**：悬停上浮10px，点击阴影扩散后淡出

---

## 快速开始

### 环境要求

- **操作系统**：Windows 10+ / macOS 10.15+ / Linux (Ubuntu 18.04+)
- **Python**：3.8 或更高版本
- **依赖管理**：pip 20.0+

### 安装步骤

```bash
# 1. 克隆仓库
git clone https://github.com/l4runner/DCR_calculator_SK
cd DCR_calculator_SK

# 2. 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动应用
python -m UI_Qtside6.MainWindow_self
```

### 依赖清单

| 包名 | 版本 | 用途 |
|------|------|------|
| PySide6 | ≥6.5.0 | Qt6 Python绑定，GUI框架 |

---

## 使用指南

### 输入规范

| 参数 | 格式                | 示例 | 解析规则                          |
|------|-------------------|------|-------------------------------|
| **参考料号** | `XXX####-XXXX-XX` | `PRT0530-XXXM-XX` | 提取4位尺寸代码（前2位宽+后2位高）           |
| **线圈规格** | `t*w*d*n`         | `0.XX*X.X*X.X*X.XX` | 线厚(mm) × 线宽(mm) × 内径(mm) × 匝数 |
| **目标料号** | 同参考料号             | `PRTXXXX-XXXM-XX` | 用于反向推演（可选）                    |
| **目标DCR** | 数值                | `XX.X` | 单位：mΩ（可选）                     |

### 操作示例

#### 场景1：正向计算（验证现有线圈DCR）

1. **输入参考料号**：`PRT0530-XXXM-XX` → 自动解析为宽5.5mm × 高3.0mm
2. **输入线圈规格**：`0.XX*X.XX*X.XX*X.XX`
3. **点击计算** → 右侧显示DCR结果（示例：XX.XX mΩ，范围XX.XX~XX.XX mΩ）

#### 场景2：反向推演（为新设计选型）

1. **完成正向计算**（需参考料号作为基准）
2. **输入目标料号**：`PRTXXXX-XXXM-XX`
3. **输入目标DCR**：`XX`（mΩ）
4. **点击计算** → 右侧显示预估规格（示例：`X.XX*X.XX*X.XX*X.XXT`）

#### 场景3：快速预设填充

- 点击右侧 **04系列** → 自动填充对应料号及规格
- 点击右侧 **05系列** → 自动填充对应料号及规格  
- 点击右侧 **06系列** → 自动填充对应料号及规格

---

## 技术架构

### 分层架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                      展示层 (Presentation)                   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐ │
│  │ MainWindow  │ │ ResultCard  │ │  FloatingPresetLabel    │ │
│  │   主窗口    │ │  结果卡片   │ │      快速预设标签       │ │
│  └─────────────┘ └─────────────┘ └─────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                      服务层 (Service)                         │
│                   calculator_service.py                       │
│              计算调度 · 结果格式化 · 异常处理                    │
├─────────────────────────────────────────────────────────────┤
│                      领域层 (Domain)                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐ │
│  │coil_calc    │ │ spec_parser │ │ Inductance_parser       │ │
│  │ DCR计算     │ │规格字符串解析│ │    电感编码解析         │ │
│  └─────────────┘ └─────────────┘ └─────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              T_core_calculator.py                       │ │
│  │              T-core磁芯几何计算                          │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```
---

### 关键技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| GUI框架 | PySide6 (Qt6) | 跨平台原生渲染 |
| 动画引擎 | QPropertyAnimation | 属性驱动动画，支持缓动曲线 |
| 设计模式 | 服务层模式 | UI与业务逻辑解耦 |
| 视觉规范 | Catppuccin Mocha | 护眼深色配色方案 |

### 核心类图

<details>
<summary>📁 点击展开核心结构</summary>

```
XIAO_LAN_Window (主窗口)
├── UnderlineEdit × 4      # 输入框（料号、规格、目标料号、目标DCR）
├── FloatingLabel_Btn × 2  # 计算按钮、清除按钮
├── FloatingPresetLabel × 3 # 右侧预设标签
└── ResultCard              # 结果展示面板（滑出式）
    ├── GradientLabel       # 渐变标题
    ├── content_label       # 正向计算结果
    └── content_label_2     # 反向推演结果
```

---
</details>

## 项目结构

<details>
<summary>📁 点击展开目录结构</summary>

```
DCR_calculator_SK/
├──  README.md                      # 项目文档
├──  requirements.txt               # 依赖配置
├──  LICENSE                        # MIT许可证
│
├──  source/                         # 核心业务逻辑层
│   ├── __init__.py
│   ├── calculator_service.py         # 服务层：计算调度与结果格式化
│   │                                  #   ├── perform_dcr_calculation()      正向计算
│   │                                  #   ├── perform_target_calculation()   反向推演
│   │                                  #   └── format_*_display()             格式化输出
│   ├── coil_calculator.py            # 算法层：DCR计算与反推
│   │                                  #   ├── calculate_dcr_with_inferred_flange()  DCR计算
│   │                                  #   ├── Reverse_coil_turns()           匝数反推
│   │                                  #   └── reverse_engineer_wire_thickness() 线径反推
│   ├── spec_parser.py                # 解析器：规格字符串与料号解析
│   │                                  #   ├── parse_coil_spec()              解析 t*w*d*n
│   │                                  #   └── extract_product_size_from_part_number()
│   ├── Inductance_parser.py          # 解析器：电感值编码解析
│   │                                  #   ├── extract_inductance_code_from_part_number()
│   │                                  #   └── parse_inductance_code()          支持 R12M/100L等格式
│   └── T_core_calculator.py          # 计算器：T-core磁芯几何计算
│                                       #   ├── estimate_flange_thickness()    摆厚估算
│                                       #   ├── estimate_compressed_coil_height() 压缩高度
│                                       #   ├── calculate_lead_length()      引脚长度
│                                       #   └── calculate_coil_length()      线圈导体长度
│
├──  UI_Qtside6/                     # UI界面层 (PySide6)
│   ├── __init__.py
│   ├── MainWindow_self.py            # 主窗口实现 (300×450)
│   │                                  #   ├── 输入框管理
│   │                                  #   ├── 计算触发逻辑
│   │                                  #   └── 结果联动展示
│   ├── ResultCard.py                 # 结果卡片组件 (280×450)
│   │                                  #   ├── 滑入/滑出动画 (250ms/200ms)
│   │                                  #   ├── 双区域结果展示
│   │                                  #   └── 渐变标题 (GradientLabel)
│   ├── UnderlineEdit.py              # Material Design输入框
│   │                                  #   ├── 浮动标签动画 (300ms)
│   │                                  #   ├── 聚焦指示线展开
│   │                                  #   └── 颜色状态变化
│   ├── FloatingBotton.py             # 浮动效果按钮
│   │                                  #   ├── 悬停上浮 (10px)
│   │                                  #   ├── 点击阴影反馈
│   │                                  #   └── 淡出动画 (50ms间隔)
│   ├── floating_preset_label.py      # 右侧快速预设标签
│   │                                  #   ├── 多系列预设
│   │                                  #   ├── 点击信号发射
│   │                                  #   └── 自动填充联动
│   ├── shining_glow_title.py         # 发光渐变标题组件
│   │                                  #   ├── 蓝青渐变动画 (40ms刷新)
│   │                                  #   ├── 正弦波动发光效果
│   │                                  #   └── 圆角背景绘制
│   └── icon_loader.py                # 图标加载工具
│
└──  outside/                        # 示例/演示
    └── PopupDialog.py                # 动画弹窗演示示例
```

</details>

---

## 算法原理

### DCR理论计算公式

$$DCR = \frac{\rho \cdot L}{A}$$

| 符号 | 含义 | 单位 | 备注 |
|------|------|------|------|
| ρ | 铜电阻率 | Ω·m | 20°C时取 1.68×10⁻⁸ |
| L | 导体总长度 | m | 线圈长度 + 引脚长度 |
| A | 导体截面积 | m² | 扁线：(厚×宽) - (4-π)R² |

### 导体长度计算

$$L_{total} = L_{coil} + L_{lead}$$

$$L_{coil} = \pi \cdot N \cdot (d_{inner} + w_{wire})$$

$$L_{lead} = 2 \cdot (\frac{width}{2} + flange) + h_{compressed}$$

### 匝数反推原理

基于电感与匝数平方成正比的关系：

$$N_2 = N_1 \cdot \sqrt{\frac{L_2}{L_1}}$$

反推结果取整后统一加 0.75 匝（工程经验值）。

### 线径反推算法

采用**二分查找**在约束范围内寻找最优解：

1. **约束条件**：`线厚 × 匝数 ≤ 产品高度 - 余量`
2. **目标函数**：`|DCR(线厚) - 目标DCR| → min`
3. **搜索区间**：`[0.08mm, 1.00mm]`，精度 `1e-6`

---

## 开发指南

### 自定义组件使用

```python
from UI_Qtside6.UnderlineEdit import UnderlineEdit
from UI_Qtside6.FloatingBotton import FloatingLabel_Btn
from UI_Qtside6.ResultCard import ResultCard

# 创建浮动标签输入框
edit = UnderlineEdit("线圈规格", parent)
edit.setText("X.XX*X.XX*X.XX*X.XX")

# 创建浮动按钮
btn = FloatingLabel_Btn("计算", icon_path="asset/icon/abacus.svg")
btn.clicked.connect(on_calculate)

# 创建结果卡片
card = ResultCard(main_window)
card.show_card()  # 触发展开动画
```

### 扩展新计算功能

1. **添加算法**：在 `source/coil_calculator.py` 中实现新函数
2. **封装服务**：在 `source/calculator_service.py` 添加服务接口
3. **UI绑定**：在 `UI_Qtside6/MainWindow_self.py` 中连接事件

示例：添加新的磁芯类型支持

```python
# source/new_core_calculator.py
def calculate_new_core_dcr(coil, product_size) -> tuple[float, float, float]:
    """新磁芯类型DCR计算"""
    # 实现计算逻辑
    return dcr_nominal, dcr_min, dcr_max
```

---

## 路线图

### 近期 (v1.1.x)
- [ ] 支持更多磁芯拓扑（PQ、RM、E型）
- [ ] 计算结果导出（CSV/PDF）
- [ ] 常用材料库（铜线 AWG 对照表）

### 中期 (v1.2.x)
- [ ] 批量计算模式（Excel导入导出）
- [ ] DCR温度特性曲线
- [ ] 历史记录与收藏功能

### 远期 (v2.0)
- [ ] 云端材料库同步
- [ ] 多语言支持（英文/日文）
- [ ] 插件系统支持第三方扩展

---

## 贡献指南

欢迎提交Issue和Pull Request！

### 开发流程

```bash
# 1. Fork 并克隆
git clone https://github.com/l4runner/DCR_calculator_SK

# 2. 创建特性分支
git checkout -b feature/new-feature

# 3. 提交更改（遵循规范）
git commit -m "feat: 添加PQ磁芯支持"

# 4. 推送并创建PR
git push origin feature/new-feature
```

### 代码规范

| 项目 | 规范 |
|------|------|
| Python代码 | PEP 8 |
| 文档字符串 | Google Style |
| 提交信息 | Conventional Commits |
| UI组件 | 保持Catppuccin配色一致性 |

---

## 许可证

本项目采用 [MIT](LICENSE) 许可证。

```
MIT License

Copyright (c) 2026 LanYupo

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

---

## 联系与反馈

| 方式 | 信息 |
|------|------|
| 项目主页 | https://github.com/l4runner/DCR_calculator_SK |
| 问题反馈 | [Issues页面](<issues链接>) |

---

<div align="center">

**如果本工具对您的工作有所帮助，请给个 Star**

[回到顶部](#dcr-calculator线圈直流电阻计算器)

</div>
