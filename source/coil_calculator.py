import math
from .spec_parser import CoilSpec
from .T_core_calculator import (
    estimate_flange_thickness, estimate_wire_corner_radius,
    calculate_lead_length,
    calculate_coil_length,
    estimate_compressed_coil_height, wire_thickness_judge,
)


def calculate_dcr_with_inferred_flange(
    coil: CoilSpec,
    product_size_mm: tuple[float, float],
) -> tuple[float, float, float]:
    tolerance_percent: float = 5.0

    turns_int = math.ceil(coil.turns)
    width, nominal_height = product_size_mm
    green_height = nominal_height - 0.15
    real_wire_thickness = coil.wire_thickness_mm * wire_thickness_judge(coil.wire_thickness_mm)
    wire_R = estimate_wire_corner_radius(coil.wire_thickness_mm)

    compressed_h = estimate_compressed_coil_height(coil.wire_thickness_mm, coil.turns)

    flange = estimate_flange_thickness(green_height, compressed_h)

    total_lead_length_mm = calculate_lead_length(width, flange, compressed_h)

    coil_length_mm = calculate_coil_length(coil.wire_width_mm, coil.inner_diameter_mm, turns_int)

    total_length_m = (coil_length_mm + total_lead_length_mm) * 1e-3

    area_m2 = ((real_wire_thickness * coil.wire_width_mm) - (4 - math.pi) * (wire_R ** 2)) * 1e-6

    resistivity_cu = 1.68e-8
    dcr_nominal = resistivity_cu * total_length_m / area_m2
    tol = tolerance_percent / 100.0
    dcr_min_1 = dcr_nominal * (1 - tol)
    dcr_max_1 = dcr_nominal * (1 + tol)

    return dcr_nominal, dcr_min_1, dcr_max_1


def Reverse_coil_turns(
    coil: CoilSpec,
    Inductance_Value: tuple[float, float],
) -> float:
    N1_int = math.ceil(coil.turns)
    L_target_uH, L_ref_uH = Inductance_Value
    N2_float = N1_int * math.sqrt(L_target_uH / L_ref_uH)
    N2_value = abs(N2_float)

    original_frac = N2_value - math.floor(N2_value)
    base_int = math.floor(N2_value)

    if original_frac < 0.35:
        base_int = max(0, base_int - 1)

    return base_int + 0.75


def reverse_engineer_wire_thickness(
        coil: CoilSpec,
        product_size_mm: tuple[float, float],
        dcr_target: float,
        target_turns: float,
        max_iterations: int = 100,
        precision: float = 1e-6,
) -> tuple[float, float]:
    width, nominal_height = product_size_mm
    green_height = nominal_height - 0.25
    Ntarget_turns = math.ceil(target_turns)
    dcr_target_ohm = dcr_target * 1e-3
    min_wt = 0.08
    max_wt = 1.00
    step = 0.01
    wt = max_wt
    real_max_wt = None

    while wt >= min_wt:
        if wt * Ntarget_turns <= green_height:
            real_max_wt = round(wt, 2)
            break
        wt = round(wt - step, 2)

    if real_max_wt is None:
        temp_coil = CoilSpec(
            wire_thickness_mm=min_wt,
            wire_width_mm=coil.wire_width_mm,
            inner_diameter_mm=coil.inner_diameter_mm,
            turns=Ntarget_turns,
        )
        dcr_min, _, _ = calculate_dcr_with_inferred_flange(temp_coil, product_size_mm)
        return min_wt, dcr_min * 1000

    def calculate_dcr_for_thickness(wire_thickness: float) -> float:
        temp_coil = CoilSpec(
            wire_thickness_mm=wire_thickness,
            wire_width_mm=coil.wire_width_mm,
            inner_diameter_mm=coil.inner_diameter_mm,
            turns=Ntarget_turns,
        )
        dcr_nom, _, _ = calculate_dcr_with_inferred_flange(temp_coil, product_size_mm)
        return dcr_nom

    dcr_min = calculate_dcr_for_thickness(real_max_wt)
    dcr_max = calculate_dcr_for_thickness(min_wt)

    if dcr_target_ohm <= dcr_min:
        return real_max_wt, dcr_min * 1000
    elif dcr_target_ohm >= dcr_max:
        return min_wt, dcr_max * 1000

    low = min_wt
    high = real_max_wt
    best_wt = None
    best_dcr = None
    min_error = float('inf')

    for i in range(max_iterations):
        mid_wt = (low + high) / 2
        dcr_mid = calculate_dcr_for_thickness(mid_wt)
        error = abs(dcr_mid - dcr_target_ohm)
        if error < min_error:
            min_error = error
            best_wt = mid_wt
            best_dcr = dcr_mid
        if error < precision:
            break

        if dcr_mid < dcr_target_ohm:
            high = mid_wt
        else:
            low = mid_wt

    if best_wt is None:
        best_wt = (low + high) / 2
        best_dcr = calculate_dcr_for_thickness(best_wt)

    return round(best_wt, 4), round(best_dcr * 1000, 3)
