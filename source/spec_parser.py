# source/spec_parser.py
import re
from typing import NamedTuple, Tuple, Optional, Dict

DEFAULT_WIDTH_MAP = {
    "04":4.1,
    "05":5.5,
    "06":6.8,
    "10":11.6,
    "17":18.2
}

class CoilSpec(NamedTuple):
    wire_thickness_mm: float
    wire_width_mm: float
    inner_diameter_mm: float
    turns: float

class Sbc(NamedTuple):
    chan_pin_chi_cun: float
    high_size: float

def parse_coil_spec(spec_str: str) -> CoilSpec:
    """解析线圈规格字符串，格式: t*w*d*n"""
    parts = [p.strip() for p in spec_str.split('*') if p.strip()]
    if len(parts) != 4:
        raise ValueError("线圈格式错误目前仅支持扁线绕线")
    try:
        t, w, d, n = map(float, parts)
        if any(x <= 0 for x in [t, w, d, n]):
            raise ValueError("所有参数必须大于0")
        return CoilSpec(t, w, d, n)
    except ValueError as e:
        raise ValueError(f"参数无效: {e}")

def extract_product_size_from_part_number(
        part_number_1: str,
        width_map: Optional[Dict[str, float]] = None
) -> Tuple[float, float]:

    part_number_2 = part_number_1.strip()
    match = re.search(r'[A-Za-z]+(\d{4})', part_number_2)
    if not match:
        raise ValueError(f"无法从料号 '{part_number_2}' 中提取4位尺寸代码（如0530）")

    size_code = match.group(1)
    if len(size_code) != 4:
        raise ValueError(f"尺寸代码必须是4位数字，得到: {size_code}")

    width_code = size_code[:2]
    height_code = size_code[2:]

    wm = width_map or DEFAULT_WIDTH_MAP

    if width_code not in wm:
        raise ValueError(
            f"不支持的宽度代码: '{width_code}'。"
            f"支持的代码: {list(wm.keys())}"
        )
    width_mm = wm[width_code]
    try:
        height_mm = float(height_code) / 10.0
    except ValueError:
        raise ValueError(f"高度代码无效: '{height_code}'，必须为数字")

    return width_mm, height_mm

# if __name__ == "__main__":
#     # 1. 输入料号
#     part_number = input("请输入料号（如 SPT0530-R27M-BA）: ").strip()
#     width, height = (
#         extract_product_size_from_part_number(part_number))
#     print(f"✅ 产品尺寸： A尺寸MAX = {width:.2f} mm, C尺寸MAX = {height:.2f} mm\n")
#
#     # 2. 输入线圈规格
#     coil_str = input("请输入线圈规格（格式:0.35*1.0*2.2*2.75）: ").strip()
#     coil = parse_coil_spec(coil_str)
#     print(f"✅ 线圈参数: 厚={coil.wire_thickness_mm}mm, 宽={coil.wire_width_mm}mm, "
#           f"内径={coil.inner_diameter_mm}mm, 匝数={coil.turns}")