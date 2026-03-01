# source/__init__.py
from .spec_parser import extract_product_size_from_part_number, parse_coil_spec, CoilSpec
from .coil_calculator import (
    calculate_dcr_with_inferred_flange,
    Reverse_coil_turns,
    reverse_engineer_wire_thickness,
)
from .T_core_calculator import (
    estimate_flange_thickness,
    central_column_height,
    estimate_wire_corner_radius,
)
from .Inductance_parser import parse_inductance_code, extract_inductance_code_from_part_number
from .calculator_service import (
    perform_dcr_calculation,
    perform_target_calculation,
    format_primary_display,
    format_target_display,
    format_error_display,
    format_no_target_display,
    format_input_error_display,
    format_target_calculation_error,
)

__all__ = [
    "extract_product_size_from_part_number",
    "parse_coil_spec",
    "calculate_dcr_with_inferred_flange",
    "reverse_engineer_wire_thickness",
    "Reverse_coil_turns",
    "estimate_flange_thickness",
    "central_column_height",
    "parse_inductance_code",
    "extract_inductance_code_from_part_number",
    "estimate_wire_corner_radius",
    "CoilSpec",
    "perform_dcr_calculation",
    "perform_target_calculation",
    "format_primary_display",
    "format_target_display",
    "format_error_display",
    "format_no_target_display",
    "format_input_error_display",
    "format_target_calculation_error",
]