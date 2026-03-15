import math


def ceiling(value: float, significance: float = 0.05) -> float:
    if significance <= 0:
        raise ValueError("significance 必须大于 0")
    return math.ceil(value / significance) * significance


def wire_thickness_judge(wire_thickness_mm: float) -> float | None:
    if wire_thickness_mm >= 0.4:
        return 0.95
    elif (wire_thickness_mm >= 0.3) and (wire_thickness_mm < 0.4):
        return 0.93
    elif (wire_thickness_mm >= 0.19) and (wire_thickness_mm < 0.3):
        return 0.90
    elif wire_thickness_mm < 0.20:
        return 0.87
    return None


def estimate_wire_corner_radius(wire_thickness_mm: float) -> float:
    if wire_thickness_mm < 0.2:
        r_factor = 0.12
    elif wire_thickness_mm < 0.4:
        r_factor = 0.15
    else:
        r_factor = 0.20
    max_r = wire_thickness_mm / 2.0
    return min(r_factor, max_r)


def add_enamel_to_wire_thickness(copper_thickness_mm: float) -> float:
    if copper_thickness_mm >= 0.50:
        return copper_thickness_mm + 0.05
    elif (copper_thickness_mm >= 0.35) and (copper_thickness_mm < 0.50):
        return copper_thickness_mm + 0.04
    elif (copper_thickness_mm >= 0.25) and (copper_thickness_mm < 0.35):
        return copper_thickness_mm + 0.03
    else:
        return copper_thickness_mm + 0.02


def estimate_compressed_coil_height(
        wire_thickness_mm: float,
        turns_1: float
) -> float:
    if wire_thickness_mm <= 0 or turns_1 <= 0:
        raise ValueError("线厚和匝数必须大于0")
    total_thickness = add_enamel_to_wire_thickness(wire_thickness_mm)
    turns_int = math.ceil(turns_1)
    ratio = wire_thickness_judge(total_thickness)
    return ratio * turns_int * total_thickness


def estimate_flange_thickness(
        product_height_mm: float,
        compressed_coil_height_mm: float
) -> float:
    if compressed_coil_height_mm >= product_height_mm:
        raise ValueError("线圈压缩厚度不能大于或等于产品总高度")
    raw_flange = (product_height_mm - compressed_coil_height_mm) / 2.0 / 0.80
    return math.ceil(raw_flange / 0.05) * 0.05


def central_column_height(
        product_height_mm: float,
) -> float:
    raw_flange = (product_height_mm + 0.15) / 0.70
    return math.ceil(raw_flange / 0.05) * 0.05


def central_column_height_2(
        coil_thickness_total: float,
        turns_2: float
) -> float:
    turns_int = math.ceil(turns_2)
    fu_zhi = add_enamel_to_wire_thickness(coil_thickness_total)
    return ceiling((fu_zhi * turns_int) / 0.89 + 0.20)


def calculate_lead_length(
    width_mm: float,
    flange_thickness_mm: float,
    compressed_coil_height_mm: float
) -> float:
    half_width = width_mm / 2.0
    return 2 * (half_width + flange_thickness_mm) + compressed_coil_height_mm


def calculate_coil_length(
    wire_width_mm: float,
    inner_diameter_mm: float,
    turns_2: int
) -> float:
    avg_diameter_mm = inner_diameter_mm + wire_width_mm
    return math.pi * turns_2 * avg_diameter_mm
