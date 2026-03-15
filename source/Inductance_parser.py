import re


def extract_inductance_code_from_part_number(part_number: str) -> str:
    if not part_number:
        return ""
    part_number = part_number.strip()
    parts = part_number.split("-")

    if len(parts) == 1:
        return part_number

    if len(parts) == 2:
        return parts[1].strip().upper()

    INDUCTANCE_KEYWORDS = ("R", "L", "UH", "NH", "MH")
    for part in parts[1:]:
        clean_part = part.strip().upper()
        if re.match(r"^[0-9]*R?[0-9]+[A-Z]$", clean_part):
            return clean_part
    for part in parts[1:]:
        clean_part = part.strip().upper()
        if any(kw in clean_part for kw in INDUCTANCE_KEYWORDS):
            return clean_part
    return parts[-2].strip().upper()


def parse_inductance_code(code: str) -> dict:
    if not code or not isinstance(code, str):
        raise ValueError("输入编码不能为空且必须是字符串")

    code = code.strip().upper()

    TOL_MAP = {
        'B': 0.1,
        'C': 0.25,
        'D': 0.5,
        'F': 1,
        'G': 2,
        'J': 5,
        'K': 10,
        'L': 15,
        'M': 20,
        'N': 30,
        'V': 25,
        'Z': 80,
    }

    match = re.search(r'^([0-9]{3})([A-Z])$', code)
    if match:
        digits, tol_char = match.groups()
        value = int(digits[:2]) * (10 ** int(digits[2]))

        tolerance = TOL_MAP.get(tol_char)
        if tolerance is None:
            raise ValueError(f"未知容差代码: {tol_char}")
    else:
        match = re.search(r'^([0-9]*R?[0-9]+)([A-Z])$', code)
        if not match:
            raise ValueError(f"无法解析电感编码: {code}")

        num_part, tol_char = match.groups()
        tolerance = TOL_MAP.get(tol_char)
        if tolerance is None:
            raise ValueError(f"未知容差代码: {tol_char}")

        if 'R' in num_part:
            integer_part, decimal_part = num_part.split('R')
            integer_part = integer_part or '0'
            decimal_part = decimal_part or '0'
            value = float(integer_part + '.' + decimal_part)
        else:
            value = float(num_part)

    tol_factor = tolerance / 100.0
    min_uh = value * (1 - tol_factor)
    max_uh = value * (1 + tol_factor)

    formatted_value = f"{value:g}"
    formatted = f"{formatted_value}±{tolerance}%"

    return {
        "value_uh": float(value),
        "tolerance_pct": float(tolerance),
        "min_uh": round(min_uh, 6),
        "max_uh": round(max_uh, 6),
        "raw_code": code,
        "formatted": formatted
    }
