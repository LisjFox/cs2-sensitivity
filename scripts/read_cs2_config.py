"""
读取 CS2 配置文件，提取鼠标灵敏度相关参数
输出 JSON 供 AI 解析
"""

import json, sys, os, re
from pathlib import Path

def find_cs2_configs():
    """查找 CS2 可能存在的所有配置文件路径"""
    user = os.environ["USERPROFILE"]
    steam_userdata = Path(r"C:\Program Files (x86)\Steam\userdata")
    
    # 如果蒸汽在其他盘，加到这里
    possible_steam_paths = [
        steam_userdata,
        Path(r"D:\Steam\userdata"),
        Path(r"D:\Games\Steam\userdata"),
    ]
    
    files = []
    
    # 在 steam userdata 里找 CS2(AppID=730) 的配置
    for steam_path in possible_steam_paths:
        if not steam_path.exists():
            continue
        for user_dir in steam_path.iterdir():
            cs2_local = user_dir / "730" / "local" / "cfg"
            if cs2_local.exists():
                main_cfg = cs2_local / "cs2_user_convars_0_slot0.vcfg"
                video_cfg = cs2_local / "cs2_video.txt"
                if main_cfg.exists():
                    files.append(main_cfg)
                if video_cfg.exists():
                    files.append(video_cfg)
                # 找到就退出，用户目录只认第一个
                break
    
    # 也检查 Documents 目录（CS2 新版可能用）
    doc_cfg = Path(user) / "Documents" / "My Games" / "Counter-Strike Global Offensive" / "cs2" / "cfg" / "config.cfg"
    if doc_cfg.exists():
        files.append(doc_cfg)
    
    return files

def parse_vcfg(filepath):
    """
    解析 CS2 的 KeyValues 格式（类似：\"key\" \"value\"）
    返回 key→value 的字典
    """
    result = {}
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                # 匹配 "key" "value" 格式
                m = re.findall(r'"([^"]+)"', line)
                if len(m) >= 2 and not line.strip().startswith("{"):
                    key = m[0]
                    val = m[1]
                    # 尝试转数字
                    try:
                        val = float(val)
                    except ValueError:
                        pass
                    result[key] = val
    except Exception as e:
        return {"error": str(e)}
    return result

def get_sensitivity_data():
    """主函数：收集所有配置数据"""
    configs = find_cs2_configs()
    if not configs:
        return {
            "found": False,
            "message": "未找到 CS2 配置文件，请确认 CS2 已安装并运行过至少一次"
        }
    
    data = {"found": True, "files_found": [str(p) for p in configs]}
    
    for cf in configs:
        cf_name = cf.name
        parsed = parse_vcfg(cf)
        
        if "sensitivity" in parsed:
            data["sensitivity"] = parsed["sensitivity"]
        if "zoom_sensitivity_ratio" in parsed:
            data["zoom_sensitivity_ratio"] = parsed["zoom_sensitivity_ratio"]
        if "setting.defaultres" in parsed:
            data["resolution_x"] = parsed["setting.defaultres"]
        if "setting.defaultresheight" in parsed:
            data["resolution_y"] = parsed["setting.defaultresheight"]
        data["source_file"] = cf_name
    
    return data

if __name__ == "__main__":
    result = get_sensitivity_data()
    print(json.dumps(result, ensure_ascii=False, indent=2))
