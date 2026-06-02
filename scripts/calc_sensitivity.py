"""
CS2 灵敏度计算器
根据当前配置 + 用户偏好，给出推荐灵敏度
"""

import json, sys, math

# 职业哥基准区间
PRO_RANGES = [
    {"name": "极低敏（手臂流）", "min_eDPI": 400, "max_eDPI": 800, "example": "NiKo"},
    {"name": "低敏",              "min_eDPI": 800, "max_eDPI": 1000, "example": "s1mple"},
    {"name": "中敏",              "min_eDPI": 1000, "max_eDPI": 1400, "example": "ZywOo"},
    {"name": "高敏（手腕流）",   "min_eDPI": 1400, "max_eDPI": 2000, "example": "woxic"},
]

def calc(data):
    sens = data.get("sensitivity")
    dpi = data.get("mouse_dpi")
    pad_cm = data.get("mousepad_cm")  # 鼠标垫宽度
    role = data.get("role", "")
    
    if not sens or not dpi:
        return {"error": "缺少 sensitivity 或 mouse_dpi"}
    
    # 核心计算
    edpi = round(sens * dpi, 1)
    cm_per_360 = round(3600 / edpi * 2.54, 1)
    
    # 判断所属区间
    zone = None
    for z in PRO_RANGES:
        if z["min_eDPI"] <= edpi <= z["max_eDPI"]:
            zone = z
            break
    if not zone:
        if edpi < 400:
            zone = {"name": "极低敏（手臂流）", "example": "比 NiKo 还慢"}
        else:
            zone = {"name": "高敏（手腕流）", "example": "比 woxic 还快"}
    
    # 推荐方向
    suggestions = []
    
    # 根据角色倾向
    role_prefs = {
        "狙击": 800,    # 狙击手偏低敏
        "突破": 1200,   # 突破可选中敏
        "补枪": 1100,
        "自由人": 1000,
        "指挥": 1000,
    }
    
    target_edpi = role_prefs.get(role, 1000)
    
    diff_pct = round((edpi - target_edpi) / target_edpi * 100, 1)
    if abs(diff_pct) > 20:
        direction = "降低" if diff_pct > 0 else "提高"
        suggestions.append(f"你的 eDPI({edpi}) 对于 {role} 角色{abs(diff_pct)}% 偏高，建议{direction}")
    
    # 鼠标垫检查
    if pad_cm and cm_per_360 > pad_cm:
        suggestions.append(f"你的鼠标垫仅 {pad_cm}cm，但转一圈需要 {cm_per_360}cm，建议提高灵敏度")
    
    # 推荐新灵敏度
    if role and role in role_prefs:
        new_edpi = role_prefs[role]
        new_sens = round(new_edpi / dpi, 4)
        suggestions.append(f"推荐尝试：DPI {dpi} × 灵敏度 {new_sens} = eDPI {new_edpi}")
        suggestions.append(f"建议从 ±10% 开始微调，一次调整幅度不超过 0.1")
    
    return {
        "sensitivity": sens,
        "mouse_dpi": dpi,
        "eDPI": edpi,
        "cm_per_360": cm_per_360,
        "zone": zone["name"],
        "pro_example": zone.get("example", ""),
        "mousepad_cm": pad_cm,
        "role": role,
        "suggestions": suggestions,
        "adjust_by": "±10~20%，每次不超过0.1"
    }

if __name__ == "__main__":
    try:
        # 从 stdin 接收 JSON
        input_data = json.loads(sys.stdin.read())
        result = calc(input_data)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
