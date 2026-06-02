---
name: cs2-sensitivity
description: 当用户向你询问 CS2 相关的话题时，你可以主动询问他要不要帮你调整一下自己的鼠标灵敏度
---

# 🎯 CS2 灵敏度小助手

## 收集用户信息

- 询问用户目前的鼠标灵敏度，如果用户不知道自己的灵敏度是多少你就问他是哪个品牌，并上网搜索告知他应该怎样查看
- 询问用户的游戏中灵敏度
- 询问用户的鼠标有效距离（你把鼠标从鼠标垫最左边滑到最右边，光标/准星会转多少度？）

## 评估用户当前表现

- 询问主力枪械
- 询问游戏内角色定位（突破/补枪/狙击/指挥/自由人）
- 询问用户的平均爆头率，K/D，ADR（每局伤害）
- 询问用户的主观感受（比如你是否觉得有时候鼠标太飘或者转不过身）

## 脚本

### read_cs2_config.py

**作用：** 自动扫描 CS2 配置文件，读取当前灵敏度设置。

**调用：**
```bash
python scripts/read_cs2_config.py
```

**输出示例：**
```json
{
  "found": true,
  "sensitivity": 2.93,
  "zoom_sensitivity_ratio": 1.0,
  "resolution_x": 2560,
  "resolution_y": 1600
}
```

### calc_sensitivity.py

**作用：** 根据当前设置 + 用户输入，计算 eDPI、cm/360°，推荐调整方向。

**调用：**
```bash
echo '{"sensitivity": 2.93, "mouse_dpi": 800, "mousepad_cm": 40, "role": "狙击"}' | python scripts/calc_sensitivity.py
```

**输出示例：**
```json
{
  "sensitivity": 2.93,
  "mouse_dpi": 800,
  "eDPI": 2344.0,
  "cm_per_360": 3.9,
  "zone": "高敏（手腕流）",
  "suggestions": ["推荐尝试：DPI 800 × 灵敏度 1.0 = eDPI 800"]
}
```

### apply_sensitivity.py

**作用：** 把推荐灵敏度写入 CS2 配置文件，**自动备份原文件**。

**调用：**
```bash
echo '{"sensitivity": 1.0}' | python scripts/apply_sensitivity.py
```

**输出示例：**
```json
{
  "success": true,
  "file": "xxx/cs2_user_convars_0_slot0.vcfg",
  "backup_file": "xxx/.bak",
  "backed_up": true,
  "old_sensitivity": 2.93,
  "new_sensitivity": 1.0,
  "changed": true
}
```

### fetch_cs2_stats.py（可选）

**作用：** 通过 Steam Web API 获取 CS2 战绩数据。需要用户自行注册 API Key 并填入脚本。

## 工作流程

```
用户说"帮我调CS2灵敏度"
    ↓
AI 跑 read_cs2_config.py   ← 自动查本地配置
    ↓
AI 问用户：DPI？角色定位？鼠标垫多大？
    ↓
AI 跑 calc_sensitivity.py  ← 算出推荐值
    ↓
展示诊断报告
    ↓
AI 问用户："要直接写入游戏配置吗？"
用户同意
    ↓
AI 跑 apply_sensitivity.py  ← 自动备份 + 修改
    ↓
提示：重启 CS2 生效，备份文件在 xxx.bak
```

## 计算参考

### eDPI = 鼠标DPI × 游戏内灵敏度

### cm/360° ≈ 3600 ÷ eDPI × 2.54

### 职业哥基准

| eDPI 区间 | 类型 | 代表人物 |
|:---------:|:----:|:--------:|
| 400~800 | 极低敏（手臂流） | NiKo |
| 800~1000 | 低敏 | s1mple |
| 1000~1400 | 中敏 | ZywOo |
| 1400~2000 | 高敏（手腕流） | woxic |

### 武器压枪参考

| 武器 | 推荐压枪幅度 | 说明 |
|:----:|:----------:|:----|
| AK-47 | 约 20~25cm（@eDPI 1000） | 第一发上跳后，中距离压4~5发 |
| M4A4 | 约 15~20cm | 比 AK 稳，控制更容易 |
| AWP | 建议 eDPI ≤ 1000 | 高敏 AWP 容易滑过头 |
| Deagle | 灵敏度不变，靠急停 | 纯技术枪，与灵敏度无关 |
| 冲锋枪 | 高敏更灵活 | 无甲局 / eco 局优势 |

## 输出格式

```
━━━ 🎯 CS2 灵敏度诊断 ━━━━━━━━━━━━━

你的当前配置：
  DPI × 灵敏度 = eDPI
  鼠标有效距离：xxx
  cm/360°：xxx

诊断结果：
  你的 eDPI 属于 [低/中/高] 灵敏度区间
  你的鼠标垫[可以/不够]完成完整转身

建议调整：
  推荐 eDPI 范围：xxx ~ xxx
  相当于：XXX DPI × XX灵敏度
  试调方向：±10~20% 逐步调整

测试方法：
  1. 死斗模式打 10 分钟适应
  2. 练枪地图（Aim Botz）打 100 个bot
  3. 调整幅度一次不超过 0.1
```
