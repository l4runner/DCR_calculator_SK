from datetime import datetime

from .spec_parser import extract_product_size_from_part_number, parse_coil_spec
from .coil_calculator import (
    calculate_dcr_with_inferred_flange,
    reverse_engineer_wire_thickness,
    Reverse_coil_turns,
)
from .Inductance_parser import parse_inductance_code, extract_inductance_code_from_part_number


def perform_dcr_calculation(part_number: str, spec_str: str) -> dict:
    product_size = extract_product_size_from_part_number(part_number)
    coil = parse_coil_spec(spec_str)

    dcr_nom, dcr_min, dcr_max = calculate_dcr_with_inferred_flange(coil, product_size)

    return {
        "part_number": part_number,
        "spec_str": spec_str,
        "product_size": product_size,
        "coil": coil,
        "wire_thickness": coil.wire_thickness_mm,
        "wire_width": coil.wire_width_mm,
        "inner_diameter": coil.inner_diameter_mm,
        "turns": coil.turns,
        "dcr_nom_m": dcr_nom * 1000,
        "dcr_min_m": dcr_min * 1000,
        "dcr_max_m": dcr_max * 1000,
        "timestamp": datetime.now(),
    }


def perform_target_calculation(
    part_number: str,
    spec_str: str,
    target_number: str,
    target_dcr: float,
) -> dict:
    product_size = extract_product_size_from_part_number(part_number)
    product_size1 = extract_product_size_from_part_number(target_number)

    inductance_part1 = extract_inductance_code_from_part_number(part_number)
    inductance_part2 = extract_inductance_code_from_part_number(target_number)

    result_inductance1 = parse_inductance_code(inductance_part1)
    result_inductance2 = parse_inductance_code(inductance_part2)

    cnp_ent = result_inductance2["value_uh"], result_inductance1["value_uh"]

    coil = parse_coil_spec(spec_str)
    n2e = Reverse_coil_turns(coil, cnp_ent)
    n3e, approximate_dcr = reverse_engineer_wire_thickness(
        coil, product_size1, target_dcr, n2e
    )

    return {
        "target_number": target_number,
        "product_size": product_size,
        "coil": coil,
        "wire_thickness": n3e,
        "wire_width": coil.wire_width_mm,
        "inner_diameter": coil.inner_diameter_mm,
        "approximate_dcr": approximate_dcr,
        "new_turns": n2e,
        "timestamp": datetime.now(),
    }


def format_primary_display(data: dict) -> str:
    return (
        f'<div style="text-align: center;">'
        f'<span style="color:#4CAF50; font-weight:bold; font-size:24px;">'
        f'DCR(P2): {data["dcr_nom_m"]:.3f} mΩ</span><br><br>'
        f'<span style="color:#4CAF50; font-size:12px;">DCR±5%:</span> '
        f'<span style="color:#e0e0e0; font-size:12px;">'
        f'{data["dcr_min_m"]:.3f} ~ {data["dcr_max_m"]:.3f} mΩ</span><br>'
        f'<span style="color:#4CAF50; font-size:12px;">参考料号:</span> '
        f'<span style="color:#e0e0e0; font-size:12px;">{data["part_number"]}</span>'
        f"</div>"
    )


def format_target_display(data: dict) -> str:
    if data.get("wire_thickness"):
        return (
            f'<div style="text-align: center;">'
            f'<span style="color:#4CAF50; font-weight:bold; font-size:18px;">'
            f'预估线圈规格: {data["wire_thickness"]:.2f}*{data["wire_width"]:.2f}*'
            f'{data["inner_diameter"]:.2f}*{data["new_turns"]:.2f}T</span><br><br>'
            f'<span style="color:#4CAF50; font-size:12px;">目标料号:</span> '
            f'<span style="color:#e0e0e0; font-size:12px;">{data["target_number"]}</span><br>'
            f'<span style="color:#4CAF50; font-size:12px;">目标DCR:</span> '
            f'<span style="color:#e0e0e0; font-size:12px;">{data.get("approximate_dcr"):.2f} mΩ</span>'
            f"</div>"
        )
    return (
        f'<div style="text-align: center;">'
        f'<span style="color:#4CAF50; font-weight:bold; font-size:18px;">预测线圈信息</span><br><br>'
        f'<span style="color:#4CAF50; font-size:12px;">目标料号:</span> '
        f'<span style="color:#e0e0e0; font-size:12px;">{data.get("target_number", "N/A")}</span><br>'
        f'<span style="color:#4CAF50; font-size:12px;">新圈数:</span> '
        f'<span style="color:#e0e0e0; font-size:12px;">{data.get("new_turns", "N/A"):.2f}T</span>'
        f"</div>"
    )


def format_error_display(message: str) -> str:
    return f"""
        <div style="padding: 20px; text-align: center;">
            <span style="color:#FF5252; font-weight:bold; font-size:12px;">
                ❌ 计算失败
            </span><br><br>
            <span style="color:#FF8A80; font-size:11px;">
                {message}
            </span>
        </div>
    """


def format_no_target_display() -> str:
    return """
        <div style="text-align: center; padding: 15px;">
            <span style="color:#B0BEC5; font-size: 14px;">
                ⏳ 等待目标输入
            </span><br>
            <span style="color:#757575; font-size: 12px;">
                请输入目标料号和目标DCR进行预测
            </span>
        </div>
    """


def format_input_error_display(error_msg: str) -> str:
    return f"""
        <div style="padding: 10px;">
            <span style="color:#FF9800; font-weight:bold; font-size:12px;">
                ⚠️ 目标输入错误
            </span><br>
            <span style="color:#FFCC80; font-size:11px;">
                {error_msg}
            </span>
        </div>
    """


def format_target_calculation_error(error_msg: str) -> str:
    return f"""
        <div style="padding: 10px;">
            <span style="color:#FF5252; font-weight:bold; font-size:12px;">
                ❌ 预测失败
            </span><br>
            <span style="color:#FF8A80; font-size:11px;">
                {error_msg}
            </span>
        </div>
    """
