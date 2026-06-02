"""
将推荐的灵敏度写入 CS2 配置文件
自动备份原文件，安全无忧
"""

import json, sys, os, shutil, re
from pathlib import Path

def find_cs2_convars():
    """找 CS2 的主配置文件"""
    steam_userdata = Path(r"C:\Program Files (x86)\Steam\userdata")
    for user_dir in steam_userdata.iterdir():
        cfg = user_dir / "730" / "local" / "cfg" / "cs2_user_convars_0_slot0.vcfg"
        if cfg.exists():
            return cfg
    return None

def apply_sensitivity(config_path, new_sens, zoom_ratio=1.0):
    """修改配置文件中的灵敏度"""
    # 1. 读原文件
    with open(config_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # 2. 备份
    backup_path = config_path.with_suffix(config_path.suffix + ".bak")
    if not backup_path.exists():
        shutil.copy2(config_path, backup_path)
        backed_up = True
    else:
        backed_up = False  # 已有备份，不覆盖

    # 3. 替换灵敏度数值
    # 匹配 "sensitivity" "xxx" 这种格式
    old_sens = None
    m = re.search(r'("sensitivity"\s+)"([\d.]+)"', content)
    if m:
        old_sens = float(m.group(2))
        content = content.replace(m.group(0), f'{m.group(1)}"{new_sens}"')

    # 4. 写回文件
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(content)

    return {
        "success": True,
        "file": str(config_path),
        "backup_file": str(backup_path),
        "backed_up": backed_up,
        "old_sensitivity": old_sens,
        "new_sensitivity": new_sens,
        "changed": old_sens != new_sens
    }

if __name__ == "__main__":
    try:
        input_data = json.loads(sys.stdin.read())
        new_sens = input_data.get("sensitivity")
        if not new_sens:
            print(json.dumps({"success": False, "error": "请传入 sensitivity 参数"}))
            sys.exit(1)

        config = find_cs2_convars()
        if not config:
            print(json.dumps({"success": False, "error": "未找到 CS2 配置文件"}))
            sys.exit(1)

        result = apply_sensitivity(config, float(new_sens))
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))
