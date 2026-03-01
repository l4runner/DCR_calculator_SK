import re

def extract_inductance_code_from_part_number(part_number: str) -> str:
    """
    从完整料号（如 'SPA0550-R50M-BA'）中提取电感编码部分（如 'R50M'）
    规则：按 '-' 分割，优先匹配正则，其次匹配含 R/L/UH/NH/MH 的段，最后回退到 parts[-2]
    """
    if not part_number:
        return ""
    part_number = part_number.strip()
    parts = part_number.split("-")

    if len(parts) == 1:
        return part_number

    if len(parts) == 2:
        return parts[1].strip().upper()

    # len(parts) >= 3：优先正则，其次关键词回退
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
    """
    解析电感值编码（如 'R12M', '100L', '2R2K' 等）

    返回：
        {
            "value_uh": float,      # 标称电感值（单位：μH）
            "tolerance_pct": float, # 容差百分比（如 20.0）
            "min_uh": float,        # 下限 = value * (1 - tol/100)
            "max_uh": float,        # 上限 = value * (1 + tol/100)
            "raw_code": str,
            "formatted": str        # 如 "0.12±20%"
        }
    """
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

# if __name__ == "__main__":
#     try:
#         code = extract_inductance_code_from_part_number("SPT0530-R27M-BA")
#         result = parse_inductance_code(code)
#         print(
#             f"{code:4} → {result['formatted']:4} | "
#             f"范围: [{result['min_uh']:.3f}, {result['max_uh']:.3f}] μH"
#         )
#     except Exception as e:
#         print(f"❌ {e}")