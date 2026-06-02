"""
[可选功能] 通过 Steam Web API 获取 CS2 战绩数据
使用前需要：注册一个免费的 Steam API Key
注册地址：https://steamcommunity.com/dev/apikey（登录 Steam，域名填 localhost）
"""

import json, sys, urllib.request, urllib.error

API_KEY_HELP = """
--- 需要 Steam API Key ---

本功能需要 Steam API Key 才能查询战绩。
请自行注册（免费，1分钟）：

  1. 打开 https://steamcommunity.com/dev/apikey
  2. 登录你的 Steam 账号
  3. 域名填写 localhost
  4. 同意条款，点注册
  5. 复制那串 Key 文字

使用方法：
  python scripts/fetch_cs2_stats.py --key xxxxxxxxxxxxxxxxxxxxx

----------------------------
"""

def get_local_steam_id():
    """从 Steam 本地配置读取你的 Steam64 ID"""
    import os, re
    login_file = r"C:\Program Files (x86)\Steam\config\loginusers.vdf"
    try:
        with open(login_file, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            m = re.search(r'"(76\d+)"', content)
            if m:
                return m.group(1)
    except:
        pass
    return None

def fetch_stats(steam_id, api_key):
    """通过 Steam API 获取 CS2 统计数据"""
    result = {"steam_id": steam_id}

    # 接口1：最近游戏记录
    try:
        url = f"https://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v1/?key={api_key}&steamid={steam_id}&count=1"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read())
        games = data.get("response", {}).get("games", [])
        for g in games:
            if g.get("appid") == 730:
                result["last_played"] = {
                    "two_weeks": round(g.get("playtime_2weeks", 0) / 60, 1),
                    "total": round(g.get("playtime_forever", 0) / 60, 1),
                }
    except Exception as e:
        result["error_playtime"] = str(e)

    # 接口2：CS2 比赛统计
    try:
        url = f"https://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v2/?appid=730&key={api_key}&steamid={steam_id}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read())
        stats = data.get("playerstats", {}).get("stats", [])
        stats_dict = {s["name"]: s["value"] for s in stats}
        result["stats"] = {
            "total_kills": stats_dict.get("total_kills", 0),
            "total_deaths": stats_dict.get("total_deaths", 0),
            "total_wins": stats_dict.get("total_wins", 0),
            "total_damage_done": stats_dict.get("total_damage_done", 0),
            "total_rounds_played": stats_dict.get("total_rounds_played", 0),
            "total_mvps": stats_dict.get("total_mvps", 0),
            "total_shots_fired": stats_dict.get("total_shots_fired", 0),
            "total_shots_hit": stats_dict.get("total_shots_hit", 0),
            "accuracy": round(stats_dict.get("total_shots_hit", 0) / max(stats_dict.get("total_shots_fired", 1), 1) * 100, 1),
            "kd_ratio": round(stats_dict.get("total_kills", 0) / max(stats_dict.get("total_deaths", 1), 1), 2),
            "total_hours": round(stats_dict.get("total_time_played", 0) / 3600, 1),
        }
    except urllib.error.HTTPError as e:
        if e.code == 403:
            result["error"] = "API Key 无效，请检查是否填写正确"
        elif e.code == 500:
            result["error"] = "未找到 CS2 统计数据，请确认已至少玩过一次 CS2 竞技模式"
        else:
            result["error"] = f"HTTP 错误 {e.code}"
    except Exception as e:
        result["error"] = str(e)

    return result

if __name__ == "__main__":
    # 从命令行参数读取 API Key
    api_key = None
    for i, arg in enumerate(sys.argv[1:]):
        if arg == "--key" and i + 1 < len(sys.argv[1:]):
            api_key = sys.argv[i + 2]
            break

    if not api_key:
        print(API_KEY_HELP)
        print(json.dumps({"success": False, "error": "缺少 --key 参数"}, ensure_ascii=False, indent=2))
        sys.exit(1)

    steam_id = get_local_steam_id()
    if not steam_id:
        steam_id = input("请输入你的 Steam64 ID（或个人资料URL中的数字）：").strip()

    result = fetch_stats(steam_id, api_key)
    print(json.dumps(result, ensure_ascii=False, indent=2))
