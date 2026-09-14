#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""读取 formMail.md 主表 → 生成 web/index.html（单文件、零外部依赖的车租车数据面板）。

用法： python build_web.py
"""
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, "formMail.md")
OUT_DIR = os.path.join(BASE, "web")
OUT = os.path.join(OUT_DIR, "index.html")

sys.stdout.reconfigure(encoding="utf-8")


def parse_md_table():
    """解析 formMail.md 中的主表（9 列），返回 dict 列表。"""
    records = []
    in_main = False
    for line in open(SRC, encoding="utf-8").read().splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        # 表头：包含「予約番号」且列数为 9
        if not in_main:
            if len(cells) == 9 and cells[0] == "予約番号":
                in_main = True
                continue
            continue
        if set("".join(cells)) <= set("- "):
            continue
        if len(cells) != 9:
            break  # 主表结束（后续是其他小节）
        if cells[0] == "予約番号":
            continue
        records.append(cells)
    return records


def split_car(raw):
    """車両列 → (车型名, 车牌/颜色信息)。车型不含末尾的括号车牌部分。"""
    raw = raw.strip()
    m = re.match(r"^(.*?)\s*[（(]([^（(]*)$", raw)
    if m and re.search(r"\d{3,4}", m.group(2)):  # 车牌号特征
        return m.group(1).strip(), m.group(2).strip()
    return raw, ""


def base_model(name):
    """车型 → 基础车系名（去掉 ハイブリッド 之类的尾注）。"""
    n = re.sub(r"\s*[（(][^（(]*[）)]\s*$", "", name).strip()
    return n or name


# 车系 → 品牌（用于车标）
BRAND = {
    "アクア": "Toyota", "ヤリス": "Toyota", "ヤリスクロス": "Toyota",
    "ノート": "Nissan", "オーラ": "Nissan",
    "スイフト": "Suzuki", "ソリオ": "Suzuki",
    "フィット": "Honda",
    "MAZDA2": "Mazda",
}


def brand_of(base):
    if base in BRAND:
        return BRAND[base]
    for k, v in BRAND.items():
        if base.startswith(k):
            return v
    return ""


def to_iso(s):
    """'2026年01月30日(金) 11:15' -> '2026-01-30 11:15'"""
    m = re.search(r"(\d{4})年(\d{1,2})月(\d{1,2})日(?:\([^)]*\))?\s*(\d{1,2}):(\d{2})", s or "")
    if m:
        y, mo, d, h, mi = m.groups()
        return "%04d-%02d-%02d %02d:%02d" % (int(y), int(mo), int(d), int(h), int(mi))
    return (s or "").strip()


def to_int(s):
    try:
        return int(str(s).replace(",", "").strip())
    except (ValueError, AttributeError):
        return 0


SVG_EXTS = ("svg",)
IMG_EXTS = ("png", "webp", "jpg", "jpeg", "gif")


def load_logo_files():
    """扫描 web/logos/，把车标在**构建期**内联进 HTML。

    返回 {品牌小写: {"kind": "svg"/"img", ...}}
    - svg：直接嵌入标记（file:// 打开也能显示，不依赖 fetch / CSS mask）
    - 位图：记录文件名，用 <img> 引用
    """
    d = os.path.join(OUT_DIR, "logos")
    out = {}
    if not os.path.isdir(d):
        return out
    for fn in sorted(os.listdir(d)):
        stem, ext = os.path.splitext(fn)
        ext = ext.lstrip(".").lower()
        key = stem.lower()
        if key in out:
            continue
        path = os.path.join(d, fn)
        if ext in SVG_EXTS:
            try:
                markup = open(path, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            # 去掉 XML 声明、DOCTYPE、注释
            markup = re.sub(r"<\?xml[^>]*\?>", "", markup)
            markup = re.sub(r"<!DOCTYPE[^>]*>", "", markup, flags=re.I)
            markup = re.sub(r"<!--.*?-->", "", markup, flags=re.S)
            markup = re.sub(r"\s+", " ", markup).strip()
            m = re.search(r"<svg\b[^>]*>", markup)
            if not m:
                continue
            tag = m.group(0)
            if "viewBox" not in tag:
                continue  # 没有 viewBox 无法自适应缩放，跳过
            # 移除固定宽高，改由 CSS 控制；去掉可能干扰的内联 style
            tag = re.sub(r'\s(?:width|height)="[^"]*"', "", tag)
            tag = re.sub(r'\sstyle="[^"]*"', "", tag)
            tag = tag[:-1] + ' preserveAspectRatio="xMidYMid meet" focusable="false">'
            markup = tag + markup[m.end():]
            # 判定是否为单色图标：没有任何「非 none / 非黑白」的显式填充色
            fills = re.findall(r'\bfill="([^"]+)"', markup)
            colored = any(
                f.strip().lower() not in ("none", "black", "#000", "#000000", "#111", "#111111",
                                          "white", "#fff", "#ffffff", "currentcolor")
                for f in fills)
            out[key] = {
                "kind": "svg", "markup": markup,
                "mono": not colored,                      # 单色 → 原色模式退化为深色+浅底
                "stroked": "stroke=" in markup,           # 描边型图标 → 同步着色
            }
        elif ext in IMG_EXTS:
            out[key] = {"kind": "img", "file": fn}
    return out


# 车型照片：web/car/ 下的 png/jpg，文件名(英文小写) → 车系（不区分 e-POWER 等后缀）
CAR_IMG_MAP = {
    "aqua": "アクア", "aura": "オーラ", "fit": "フィット", "mazda2": "MAZDA2",
    "note_e-power": "ノート", "note": "ノート", "solio": "ソリオ", "swift": "スイフト",
    "yaris": "ヤリス", "yariscross": "ヤリスクロス", "yaris_cross": "ヤリスクロス",
}
CAR_IMG_EXTS = ("png", "jpg", "jpeg", "webp")


def norm_key(s):
    """车系名归一化：小写、去空格/连字符、去括号内容与 e-POWER / ハイブリッド 等后缀。

    用于让 'オーラ e-POWER' 与 'オーラ' 视为同一车系。
    """
    s = (s or "").lower()
    s = re.sub(r"[\s_\-−]+", "", s)
    s = re.sub(r"[（(][^（(]*[）)]", "", s)
    s = s.replace("epower", "").replace("eパワー", "")
    s = s.replace("ハイブリッド", "").replace("hybrid", "")
    return s


def load_car_images(bases):
    """扫描 web/car/，把车型照片在构建期关联成 {实际车系名: 'car/文件名'}。

    bases：数据中实际出现的车系名集合（如 'オーラ e-POWER'）。
    文件名经 CAR_IMG_MAP 转成车系后，再用 norm_key 归一化匹配真实车系名。
    运行时用相对路径 <img src> 显示（file:// 双击即可，无需内联）。
    """
    d = os.path.join(OUT_DIR, "car")
    out = {}
    if not os.path.isdir(d):
        return out, []
    index = {}
    for b in bases:
        index.setdefault(norm_key(b), b)
    files = sorted(os.listdir(d),
                   key=lambda f: (os.path.splitext(f)[0].lower(),
                                  0 if os.path.splitext(f)[1].lower() == ".png" else 1))
    unmatched = []
    for fn in files:
        stem, ext = os.path.splitext(fn)
        if ext.lstrip(".").lower() not in CAR_IMG_EXTS:
            continue
        target = CAR_IMG_MAP.get(stem.lower())
        if not target:
            unmatched.append(fn)
            continue
        base = index.get(norm_key(target)) or (target if target in bases else None)
        if not base:
            unmatched.append(fn)
            continue
        if base in out:
            continue                      # 同名多格式时优先 png（已排序）
        out[base] = "car/" + fn
    return out, unmatched


def main():
    rows = parse_md_table()
    if not rows:
        print("未从 formMail.md 解析到数据")
        return 1

    recs = []
    for c in rows:
        model, plate = split_car(c[5])
        base = base_model(model)
        recs.append({
            "no": c[0],
            "booked": c[1],
            "start": to_iso(c[2]),
            "end": to_iso(c[3]),
            "station": c[4],
            "car": model,
            "base": base,
            "brand": brand_of(base),
            "plate": plate,
            "minutes": to_int(c[6]),
            "km": to_int(c[7]),
            "yen": to_int(c[8]),
        })

    recs.sort(key=lambda r: r["start"])

    logos = load_logo_files()
    bases = {r["base"] for r in recs}
    car_imgs, unmatched = load_car_images(bases)
    payload = {"records": recs}

    html = TEMPLATE.replace("__DATA__", json.dumps(payload, ensure_ascii=False))
    html = html.replace("__LOGOS__", json.dumps(logos, ensure_ascii=False))
    html = html.replace("__CARIMGS__", json.dumps(car_imgs, ensure_ascii=False))

    os.makedirs(OUT_DIR, exist_ok=True)
    # 车标图片覆盖目录：放入 toyota.png / nissan.png / suzuki.png / honda.png / mazda.png
    # （小写品牌名）即可替换内联 SVG；文件不存在时自动回退到 SVG。
    os.makedirs(os.path.join(OUT_DIR, "logos"), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)

    models = sorted({r["car"] for r in recs})
    print(f"已生成 {OUT}")
    print(f"  行程 {len(recs)} 条 / 车型 {len(models)} 种")
    print(f"  合计 {sum(r['minutes'] for r in recs)} 分 / "
          f"{sum(r['km'] for r in recs)} km / {sum(r['yen'] for r in recs):,} 円")
    if logos:
        print(f"  已内联车标 {len(logos)} 个：" +
              ", ".join(f"{k}({v['kind']})" for k, v in sorted(logos.items())))
    else:
        print("  未找到 web/logos/ 下的车标，全部使用内置绘制图标")
    if car_imgs:
        print(f"  已关联车型照片 {len(car_imgs)}/{len(bases)} 个车系：" +
              ", ".join(f"{k}→{v}" for k, v in sorted(car_imgs.items())))
    miss = sorted(bases - set(car_imgs))
    if miss:
        print(f"  缺图车系：{', '.join(miss)}")
    if unmatched:
        print(f"  未识别的图片文件：{', '.join(unmatched)}")
    return 0


TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Times CAR · 我的租车数据面板</title>
<style>
:root{
  --bg:#070b15; --panel:rgba(255,255,255,.05); --line:rgba(255,255,255,.10);
  --line2:rgba(255,255,255,.16); --txt:#e9edf6; --dim:#8b93ac;
  --c1:#3dd7e6; --c2:#9b8cf0; --c3:#f06ba0; --c4:#f0cd5a; --c5:#5fd99a;
  --glass:rgba(255,255,255,.055); --glassed:blur(22px) saturate(140%);
  --hi:inset 0 1px 0 rgba(255,255,255,.08);
  --shadow:0 8px 32px rgba(0,0,0,.35);
}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{
  background:var(--bg); color:var(--txt); min-height:100vh; overflow-x:hidden;
  font-family:"Segoe UI","PingFang SC","Microsoft YaHei",-apple-system,sans-serif;
  -webkit-font-smoothing:antialiased;
}
/* ---------- 背景光斑（克制的磨砂光晕） ---------- */
.aurora{position:fixed;inset:0;z-index:0;overflow:hidden;pointer-events:none;
  background:radial-gradient(120% 80% at 50% -10%,rgba(60,90,150,.18),transparent 60%)}
.aurora span{position:absolute;border-radius:50%;filter:blur(130px);opacity:.16;animation:float 34s ease-in-out infinite}
.aurora span:nth-child(1){width:560px;height:560px;background:#2f7fb8;top:-200px;left:-160px}
.aurora span:nth-child(2){width:520px;height:520px;background:#6b5fb0;top:18%;right:-220px;animation-delay:-11s}
.aurora span:nth-child(3){width:480px;height:480px;background:#a85a86;bottom:-220px;left:30%;animation-delay:-22s}
@keyframes float{0%,100%{transform:translate(0,0) scale(1)}33%{transform:translate(40px,-30px) scale(1.06)}66%{transform:translate(-30px,26px) scale(.96)}}
body::before{content:"";position:fixed;inset:0;z-index:1;pointer-events:none;
  background-image:linear-gradient(rgba(255,255,255,.022) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.022) 1px,transparent 1px);
  background-size:60px 60px;mask-image:radial-gradient(ellipse 80% 60% at 50% 0%,#000 35%,transparent 100%)}
.wrap{position:relative;z-index:2;max-width:1280px;margin:0 auto;padding:0 24px 80px}

/* ---------- Hero ---------- */
header{padding:76px 0 40px;text-align:center}
.tag{display:inline-flex;align-items:center;gap:8px;padding:7px 18px;border-radius:999px;
  border:1px solid var(--line);background:var(--panel);backdrop-filter:blur(12px);
  font-size:12px;letter-spacing:.22em;color:var(--c1);text-transform:uppercase}
.tag i{width:6px;height:6px;border-radius:50%;background:var(--c1);box-shadow:0 0 12px var(--c1);animation:pulse 1.8s infinite}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.35;transform:scale(.7)}}
h1{font-size:clamp(34px,6vw,62px);font-weight:800;letter-spacing:-.02em;margin:22px 0 14px;line-height:1.1}
.grad{background:linear-gradient(100deg,#bfe6ff,#9fb4f5 55%,#d3bef0);-webkit-background-clip:text;background-clip:text;color:transparent}
.sub{color:var(--dim);font-size:15px}
.sub b{color:var(--txt)}

/* ---------- KPI ---------- */
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:18px;margin-top:44px}
.kpi{position:relative;padding:26px 24px;border-radius:20px;border:1px solid var(--line);
  background:var(--glass);backdrop-filter:var(--glassed);box-shadow:var(--shadow),var(--hi);
  overflow:hidden;transition:.35s}
.kpi:hover{transform:translateY(-5px);border-color:var(--line2)}
.kpi::after{content:"";position:absolute;inset:0 0 auto 0;height:2px;background:linear-gradient(90deg,transparent,var(--ac),transparent);opacity:.55}
.kpi .lb{font-size:12px;color:var(--dim);letter-spacing:.1em;text-transform:uppercase}
.kpi .vl{font-size:36px;font-weight:800;margin-top:10px;font-variant-numeric:tabular-nums;line-height:1}
.kpi .vl small{font-size:16px;font-weight:600;color:var(--dim);margin-left:4px}
.kpi .ex{margin-top:8px;font-size:12.5px;color:var(--dim)}

/* ---------- 品牌图例 ---------- */
.brands{display:flex;justify-content:center;flex-wrap:wrap;gap:12px;margin-top:30px}
.blogo{display:inline-flex;align-items:center;gap:9px;padding:8px 15px 8px 9px;border-radius:999px;
  border:1px solid var(--line);background:var(--glass);backdrop-filter:var(--glassed);
  box-shadow:var(--hi);transition:.3s}
.blogo:hover{border-color:var(--bc);background:color-mix(in srgb,var(--bc) 12%,transparent);transform:translateY(-3px)}
.blogo b{font-size:13px;font-weight:700}
.blogo i{font-style:normal;font-size:11px;color:var(--dim);font-variant-numeric:tabular-nums}

/* ---------- Panel ---------- */
.panel{margin-top:56px;opacity:0;transform:translateY(26px);transition:.7s cubic-bezier(.2,.7,.3,1)}
.panel.in{opacity:1;transform:none}
.ph{display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap;margin-bottom:22px}
.ph h2{font-size:23px;font-weight:700;display:flex;align-items:center;gap:12px}
.ph h2::before{content:"";width:4px;height:22px;border-radius:3px;background:linear-gradient(var(--c1),var(--c2))}
.ph .hint{color:var(--dim);font-size:13px}

/* ---------- 开关 ---------- */
.segs{display:flex;gap:10px;flex-wrap:wrap}
.seg{display:inline-flex;padding:4px;border-radius:999px;border:1px solid var(--line);background:var(--panel);backdrop-filter:blur(12px)}
.seg button{border:0;background:transparent;color:var(--dim);padding:8px 18px;border-radius:999px;
  font-size:13px;cursor:pointer;transition:.25s;font-family:inherit}
.seg button.on{color:#0a1424;font-weight:700;background:linear-gradient(100deg,#cfeeff,#b9c8ff);box-shadow:var(--hi)}

/* ---------- 车型卡片 ---------- */
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:20px}
.card{position:relative;padding:24px;border-radius:22px;border:1px solid var(--line);
  background:var(--glass);backdrop-filter:var(--glassed);box-shadow:var(--shadow),var(--hi);
  overflow:hidden;transition:.4s cubic-bezier(.2,.7,.3,1)}
.card:hover{transform:translateY(-6px);border-color:var(--line2);box-shadow:0 18px 44px -20px var(--cc)}
.card::before{content:"";position:absolute;top:-70px;right:-70px;width:190px;height:190px;border-radius:50%;
  background:var(--cc);filter:blur(64px);opacity:.12;transition:.4s}
.card:hover::before{opacity:.2;transform:scale(1.12)}
.card-top{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;position:relative;z-index:2;margin-bottom:14px}
.card-top .hd{flex:1}
.rk{font-size:42px;font-weight:900;line-height:1;color:transparent;-webkit-text-stroke:1.5px rgba(255,255,255,.18);transform:translateY(-3px);opacity:.85}
.card-bg{position:absolute;inset:0;z-index:0;border-radius:inherit;overflow:hidden}
.card-bg img{position:absolute;right:-3%;top:9%;width:82%;height:90%;object-fit:contain;opacity:.9;filter:drop-shadow(0 10px 22px rgba(0,0,0,.55))}
.card-bg::after{content:"";position:absolute;inset:0;background:linear-gradient(105deg,rgba(7,11,21,.93) 24%,rgba(7,11,21,.6) 58%,rgba(7,11,21,.2) 100%)}
.card-body{position:relative;z-index:2;display:flex;flex-direction:column;gap:14px}
.hd{display:flex;align-items:center;gap:13px;position:relative}

/* ---------- 车标 ---------- */
.logo{flex:0 0 auto;width:42px;height:42px;position:relative;display:grid;place-items:center;
  border-radius:12px;border:1px solid var(--line);color:var(--bc);
  background:linear-gradient(150deg,rgba(255,255,255,.11),rgba(255,255,255,.03))}
.logo .fb{width:76%;height:76%;overflow:visible;
  filter:drop-shadow(0 0 7px color-mix(in srgb,var(--bc) 55%,transparent))}
/* 真实车标（web/logos/ 内联）：显示 .pic，隐藏内置绘制的 .fb */
.logo.real .fb{display:none}
.logo .pic{position:absolute;inset:12%;width:76%;height:76%;
  display:grid;place-items:center;pointer-events:none}
.logo .pic svg{width:100%;height:100%;overflow:visible;
  filter:drop-shadow(0 0 7px color-mix(in srgb,var(--bc) 50%,transparent))}
.logo .pic img{width:100%;height:100%;object-fit:contain;
  filter:drop-shadow(0 0 8px color-mix(in srgb,var(--bc) 50%,transparent))}
/* 品牌色模式（默认）：强制品牌色着色，覆盖 SVG 自身的黑/灰/none
   —— 解决「无 fill 默认黑」或「fill=none」在深色背景上不可见的问题 */
.logo.real .pic svg,.logo.real .pic svg *{fill:var(--bc)}
.logo.real .pic.stroked svg,.logo.real .pic.stroked svg *{
  fill:none;stroke:var(--bc);stroke-width:1.4%}
/* 原色模式：单色图标 → 深色图标 + 浅色徽章底（保证可见）；
             彩色图标 → 保留自身配色 */
body.orig .logo.real .pic.mono svg,body.orig .logo.real .pic.mono svg *{fill:#0f172a;stroke:none}
body.orig .logo.real .pic.mono{background:#f2f4f8;border-radius:9px}
body.orig .logo.real .pic.mono svg{filter:none}
body.orig .logo.real .pic:not(.mono) svg,body.orig .logo.real .pic:not(.mono) svg *{fill:revert;stroke:revert}
.logo.sm{width:26px;height:26px;border-radius:8px}
.card:hover .logo{border-color:var(--bc);box-shadow:0 0 22px -4px var(--bc)}

.nm{font-size:22px;font-weight:800;letter-spacing:.01em;position:relative}
.nm .en{display:block;font-size:11.5px;color:var(--dim);font-weight:600;letter-spacing:.14em;margin-top:5px;text-transform:uppercase}
.chips{display:flex;flex-wrap:wrap;gap:6px;margin-top:12px;position:relative}
.chip{font-size:11px;padding:4px 10px;border-radius:8px;border:1px solid var(--line);
  background:rgba(255,255,255,.05);color:var(--dim)}
.chip.b{color:var(--cc);border-color:var(--cc);background:color-mix(in srgb,var(--cc) 14%,transparent)}
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:20px;position:relative}
.stat{padding:12px;border-radius:14px;background:rgba(0,0,0,.28);border:1px solid rgba(255,255,255,.06);text-align:center}
.stat .v{font-size:20px;font-weight:800;font-variant-numeric:tabular-nums;color:var(--cc)}
.stat .k{font-size:10.5px;color:var(--dim);margin-top:3px;letter-spacing:.06em}
.bars{margin-top:18px;display:flex;flex-direction:column;gap:11px;position:relative}
.bar .t{display:flex;justify-content:space-between;font-size:11.5px;color:var(--dim);margin-bottom:5px}
.bar .t b{color:var(--txt);font-variant-numeric:tabular-nums;font-weight:600}
.track{height:7px;border-radius:99px;background:rgba(255,255,255,.08);overflow:hidden}
.fill{height:100%;width:0;border-radius:99px;transition:width 1.2s cubic-bezier(.2,.8,.2,1)}
.card .foot{display:flex;justify-content:space-between;margin-top:18px;padding:12px 14px 2px;border-radius:12px;
  background:rgba(7,11,21,.42);backdrop-filter:blur(4px);border-top:1px dashed rgba(255,255,255,.14);
  font-size:12px;color:var(--dim);position:relative;z-index:2}
.card .foot b{color:var(--txt);font-variant-numeric:tabular-nums}

/* ---------- 对比图 ---------- */
.chart{display:flex;flex-direction:column;gap:13px;padding:26px;border-radius:22px;
  border:1px solid var(--line);background:var(--glass);backdrop-filter:var(--glassed);
  box-shadow:var(--shadow),var(--hi)}
.crow{display:grid;grid-template-columns:170px 1fr 128px;align-items:center;gap:14px;font-size:13.5px}
.crow .cn{display:flex;align-items:center;gap:9px;color:var(--txt);font-weight:600;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.crow .cv{text-align:right;font-variant-numeric:tabular-nums;font-weight:700;color:var(--dim)}
.crow .cv b{color:var(--txt);font-size:15px}
.ctrack{height:26px;border-radius:9px;background:rgba(255,255,255,.055);overflow:hidden;position:relative}
.cfill{height:100%;width:0;border-radius:9px;transition:width 1.1s cubic-bezier(.2,.8,.2,1);
  display:flex;align-items:center;justify-content:flex-end;padding-right:10px;font-size:11px;font-weight:700;color:#04121a}
.crow:hover .ctrack{background:rgba(255,255,255,.11)}

/* ---------- 月度 ---------- */
.months{display:grid;grid-template-columns:repeat(auto-fit,minmax(74px,1fr));gap:14px;align-items:end;
  padding:28px 24px 18px;border-radius:22px;border:1px solid var(--line);background:var(--glass);
  backdrop-filter:var(--glassed);box-shadow:var(--shadow),var(--hi);min-height:250px}
.mcol{display:flex;flex-direction:column;align-items:center;gap:9px;justify-content:flex-end;height:100%}
.mbar{width:100%;border-radius:10px 10px 4px 4px;background:linear-gradient(180deg,var(--c1),var(--c2));
  position:relative;transition:.5s;min-height:4px;cursor:default}
.mcol:hover .mbar{filter:brightness(1.25);transform:scaleX(1.1)}
.mbar span{position:absolute;top:-22px;left:50%;transform:translateX(-50%);font-size:10.5px;
  color:var(--dim);white-space:nowrap;opacity:0;transition:.3s;font-variant-numeric:tabular-nums}
.mcol:hover .mbar span{opacity:1}
.mlb{font-size:11.5px;color:var(--dim);font-variant-numeric:tabular-nums}

/* ---------- 明细 ---------- */
.tools{display:flex;gap:12px;flex-wrap:wrap;align-items:center;margin-bottom:16px}
input[type=search]{flex:1;min-width:220px;padding:12px 18px;border-radius:14px;border:1px solid var(--line);
  background:var(--glass);color:var(--txt);font-size:14px;font-family:inherit;backdrop-filter:var(--glassed);
  box-shadow:var(--hi);outline:none;transition:.25s}
input[type=search]:focus{border-color:var(--c1);box-shadow:0 0 0 3px rgba(61,215,230,.14)}
input[type=search]::placeholder{color:#5c6480}
.tbox{border:1px solid var(--line);border-radius:18px;overflow:auto;background:var(--glass);backdrop-filter:var(--glassed);box-shadow:var(--shadow),var(--hi);max-height:600px}
table{width:100%;border-collapse:collapse;font-size:13px}
th{position:sticky;top:0;background:rgba(12,18,38,.82);backdrop-filter:blur(8px);padding:14px 16px;text-align:left;font-size:11.5px;
  color:var(--c1);letter-spacing:.1em;text-transform:uppercase;cursor:pointer;white-space:nowrap;user-select:none;z-index:2}
th:hover{color:#fff}
th::after{content:" ⇅";opacity:.4;font-size:10px}
td{padding:13px 16px;border-top:1px solid rgba(255,255,255,.055);white-space:nowrap;font-variant-numeric:tabular-nums}
tbody tr{transition:.2s}
tbody tr:hover{background:rgba(255,255,255,.055)}
td.n{text-align:right;font-weight:600}
.pill{display:inline-block;padding:3px 10px;border-radius:999px;font-size:11.5px;
  background:rgba(34,211,238,.14);color:var(--c1);border:1px solid rgba(34,211,238,.3)}
td.car{color:var(--txt);font-weight:600}
td.mut{color:var(--dim)}
td.car .cw{display:inline-flex;align-items:center;gap:9px}

footer{text-align:center;padding:52px 0 10px;color:var(--dim);font-size:12.5px;position:relative;z-index:2}
footer b{background:linear-gradient(100deg,var(--c1),var(--c2) 45%,var(--c3));-webkit-background-clip:text;background-clip:text;color:transparent}

@media(max-width:760px){
  .crow{grid-template-columns:100px 1fr 92px;font-size:12px}
  .kpi .vl{font-size:28px}
  .wrap{padding:0 14px 60px}
}
</style>
</head>
<body>
<div class="aurora"><span></span><span></span><span></span></div>

<div class="wrap">
  <header>
    <div class="tag"><i></i>Times Car Rental Analytics</div>
    <h1>My <span class="grad">Times</span></h1>
    <p class="sub" id="sub"></p>
    <div class="kpis" id="kpis"></div>
  </header>

  <section class="panel">
    <div class="ph">
      <h2>车型画像</h2>
      <div class="segs">
        <div class="seg" id="seg">
          <button data-m="base" class="on">按车系合并</button>
          <button data-m="car">按具体型号</button>
        </div>
        <div class="seg" id="tint" title="切换 web/logos/ 下真实车标的着色方式">
          <button data-t="1" class="on">车标·品牌色</button>
          <button data-t="0">车标·原色</button>
        </div>
      </div>
    </div>
    <div class="grid" id="grid"></div>
  </section>

  <section class="panel">
    <div class="ph">
      <h2>车型对比</h2>
      <div class="seg" id="metric">
        <button data-k="km" class="on">走行距離</button>
        <button data-k="yen">請求金額</button>
        <button data-k="minutes">利用時間</button>
        <button data-k="count">利用回数</button>
      </div>
    </div>
    <div class="chart" id="chart"></div>
  </section>

  <section class="panel">
    <div class="ph"><h2>月度趋势</h2><span class="hint">柱高 = 当月請求金額</span></div>
    <div class="months" id="months"></div>
  </section>

  <section class="panel">
    <div class="ph"><h2>行程明细</h2><span class="hint" id="cnt"></span></div>
    <div class="tools">
      <input type="search" id="q" placeholder="搜索车型 / 站点 / 予約番号…">
      <div class="seg" id="sortseg">
        <button data-s="start" class="on">按时间</button>
        <button data-s="yen">按金额</button>
        <button data-s="km">按距离</button>
      </div>
    </div>
    <div class="tbox">
      <table>
        <thead><tr>
          <th data-c="start">利用開始</th><th data-c="car">車両</th><th data-c="station">ステーション</th>
          <th data-c="minutes">利用時間</th><th data-c="km">走行距離</th><th data-c="yen">請求金額</th>
        </tr></thead>
        <tbody id="tb"></tbody>
      </table>
    </div>
  </section>

  <footer>Powered by <b>Times CAR</b> · 数据来自 mail 预约邮件 × site 利用明细</footer>
</div>

<script>
const DATA = __DATA__;
const R = DATA.records;
const PALETTE = ['#22d3ee','#a855f7','#ff3d81','#facc15','#4ade80','#fb923c','#60a5fa','#f472b6','#34d399','#c084fc','#f87171'];
const MODEL_EN = {
  'アクア':'AQUA','オーラ':'AURA','スイフト':'SWIFT','ソリオ':'SOLIO','ノート':'NOTE',
  'フィット':'FIT','ヤリスクロス':'YARIS CROSS','ヤリス':'YARIS','MAZDA2':'MAZDA2'
};
/* 英文名查找：先精确匹配，再去掉括号后缀与 e-POWER / ハイブリッド 后重试 */
const modelEn = n => MODEL_EN[n]
  || MODEL_EN[(n||'').replace(/\s*[（(][^（(]*[）)]\s*/g,'').replace(/\s*e-?POWER\s*/gi,' ').trim()]
  || n;

/* ---------- 车标（内联 SVG；若 web/logos/<brand>.png 存在则优先用图片） ---------- */
const BRAND_COLOR = {Toyota:'#E2111A', Nissan:'#C9CED6', Honda:'#F26522', Suzuki:'#0F62C4', Mazda:'#00AEEF'};
const BRAND_SVG = {
  Toyota:`<svg class="fb" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="3.4">
    <ellipse cx="32" cy="32" rx="29" ry="18"/>
    <ellipse cx="32" cy="27" rx="8.5" ry="19"/>
    <ellipse cx="32" cy="40" rx="20" ry="8.5"/></svg>`,
  Nissan:`<svg class="fb" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="3.4">
    <circle cx="32" cy="32" r="27"/>
    <rect x="5" y="24.5" width="54" height="15" fill="currentColor" stroke="none"/>
    <text x="32" y="35" text-anchor="middle" font-size="10.5" font-weight="800"
      fill="#0b1020" font-family="Arial,sans-serif" letter-spacing="0.5">NISSAN</text></svg>`,
  Suzuki:`<svg class="fb" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="6"
    stroke-linecap="round">
    <path d="M47 19c-2.5-4-7.5-6.5-14-6.5C22 12.5 14.5 17.5 14.5 25.5s4.5 10 14 12l5.5 1
      c5.5 1 8 3 8 6.5s-4.5 7-12 7c-7.5 0-13-3.5-14-9"/></svg>`,
  Honda:`<svg class="fb" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="3.4"
    stroke-linejoin="round">
    <path d="M14 15h36l6 34H8z"/>
    <path d="M21 26v14M43 26v14M21 33h22" stroke-width="5"/></svg>`,
  Mazda:`<svg class="fb" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="3.4"
    stroke-linejoin="round" stroke-linecap="round">
    <circle cx="32" cy="32" r="27"/>
    <path d="M17 43V24l15 13 15-13v19" stroke-width="4.6"/>
    <path d="M32 37v11" stroke-width="3"/></svg>`
};
function logo(b, sm){
  if(!b) return '';
  return `<span class="logo${sm?' sm':''}" data-b="${b}" style="--bc:${BRAND_COLOR[b]||'#22d3ee'}" title="${b}">`
    + (BRAND_SVG[b]||'') + `</span>`;
}

/* web/logos/ 下的真实车标（构建期已读入，file:// 直接打开也能显示） */
const LOGO_FILES = __LOGOS__;
const CAR_IMGS = __CARIMGS__;                          // {车系: "car/xxx.png"} 车型照片（相对路径，file:// 可直接显示）
let TINT = true;                                       // true=品牌色 / false=原色（浅色底衬托）
try{ const v = localStorage.getItem('logo-tint'); if(v!==null) TINT = v === '1'; }catch(e){}

function applyLogo(el){
  const f = LOGO_FILES[(el.dataset.b||'').toLowerCase()];
  if(!f) return;                                       // 无车标文件 → 保留内置绘制图标
  el.classList.add('real');
  if(f.kind === 'svg'){
    el.innerHTML = `<span class="pic${f.mono?' mono':''}${f.stroked?' stroked':''}">${f.markup}</span>`
      + (el.dataset.fb||'');
  }else{
    el.innerHTML = `<img class="pic" src="logos/${f.file}" alt="${el.dataset.b}">` + (el.dataset.fb||'');
  }
}
function refreshLogos(){
  document.querySelectorAll('.logo[data-b]').forEach(applyLogo);
  document.body.classList.toggle('orig', !TINT);
}
function upgradeLogos(root){
  (root||document).querySelectorAll('.logo[data-b]').forEach(el=>{
    if(el.dataset.done) return;
    el.dataset.done = '1';
    el.dataset.fb = el.innerHTML;                      // 记住内置图标，供原色模式兜底
    applyLogo(el);
  });
  (root||document).querySelectorAll('.logo').forEach(el=>el.classList.toggle('real',
    !!LOGO_FILES[(el.dataset.b||'').toLowerCase()]));
}
const $ = s => document.querySelector(s);
const fmt = n => (n||0).toLocaleString('en-US');
const hm  = m => Math.floor(m/60) + 'h' + String(m%60).padStart(2,'0') + 'm';

/* ---------- 汇总 ---------- */
const T = R.reduce((a,r)=>({n:a.n+1,km:a.km+r.km,yen:a.yen+r.yen,min:a.min+r.minutes}),{n:0,km:0,yen:0,min:0});
const dates = R.map(r=>r.start.slice(0,10)).sort();
$('#sub').innerHTML = `${dates[0]} → ${dates[dates.length-1]} · 共 <b>${T.n}</b> 次行程 · `
  + `<b>${new Set(R.map(r=>r.base)).size}</b> 个车系 · 总支出 <b>¥${fmt(T.yen)}</b>`;

/* 品牌图例 */
(function(){
  const bs = [...new Set(R.map(r=>r.brand).filter(Boolean))].sort();
  const el = document.createElement('div');
  el.className = 'brands';
  el.innerHTML = bs.map(b=>`<span class="blogo" style="--bc:${BRAND_COLOR[b]}">
    ${logo(b)}<b>${b}</b><i>${R.filter(r=>r.brand===b).length}次</i></span>`).join('');
  document.querySelector('header').appendChild(el);
  upgradeLogos(el);
})();

const KPI = [
  ['总行程', T.n, '次', `平均 ¥${fmt(Math.round(T.yen/T.n))} / 次`, '#22d3ee'],
  ['总行驶距离', T.km, 'km', `平均 ${(T.km/T.n).toFixed(1)} km / 次`, '#a855f7'],
  ['总请求金额', T.yen, '円', `约 ¥${fmt(Math.round(T.yen/ (T.min/60)))} / 小时`, '#ff3d81'],
  ['总利用时间', Math.round(T.min/60), '小时', `${hm(T.min)} 累计`, '#facc15'],
];
$('#kpis').innerHTML = KPI.map(([l,v,u,e,c])=>`
  <div class="kpi" style="--ac:${c}">
    <div class="lb">${l}</div>
    <div class="vl"><span class="num" data-to="${v}">0</span><small>${u}</small></div>
    <div class="ex">${e}</div>
  </div>`).join('');

/* ---------- 数字滚动 ---------- */
const io = new IntersectionObserver(es=>es.forEach(e=>{
  if(!e.isIntersecting) return;
  const el = e.target;
  io.unobserve(el);
  if(el.classList.contains('num')){
    const to = +el.dataset.to, t0 = performance.now(), d = 1400;
    (function step(t){
      const p = Math.min((t-t0)/d,1), e2 = 1-Math.pow(1-p,3);
      el.textContent = Math.round(to*e2).toLocaleString('en-US');
      if(p<1) requestAnimationFrame(step);
    })(t0);
  }else{
    el.classList.add('in');
    el.querySelectorAll('.fill,.cfill').forEach((f,i)=>setTimeout(()=>f.style.width=f.dataset.w,(i*40)+120));
    el.querySelectorAll('.mbar').forEach((b,i)=>setTimeout(()=>b.style.height=b.dataset.h,i*55));
  }
}),{threshold:.18});
document.querySelectorAll('.panel').forEach(p=>io.observe(p));
document.querySelectorAll('.num').forEach(n=>io.observe(n));

/* ---------- 分组 ---------- */
function groupBy(mode){
  const m = new Map();
  R.forEach(r=>{
    const k = r[mode];
    if(!m.has(k)) m.set(k,{name:k,brand:r.brand,base:r.base,variants:new Set(),stations:new Set(),n:0,km:0,yen:0,minutes:0,first:r.start,last:r.start});
    const g = m.get(k);
    g.variants.add(r.car); g.stations.add(r.station);
    g.n++; g.km+=r.km; g.yen+=r.yen; g.minutes+=r.minutes;
    if(r.start<g.first) g.first=r.start;
    if(r.start>g.last)  g.last=r.start;
  });
  return [...m.values()].sort((a,b)=>b.yen-a.yen);
}

let MODE='base', METRIC='km';
function renderCards(){
  const g = groupBy(MODE);
  const maxKm = Math.max(...g.map(x=>x.km)), maxYen = Math.max(...g.map(x=>x.yen));
  $('#grid').innerHTML = g.map((x,i)=>{
    const c = PALETTE[i%PALETTE.length];
    const vs = [...x.variants].filter(v=>v!==x.name);
    const bg = CAR_IMGS[x.base]
      ? `<div class="card-bg"><img src="${CAR_IMGS[x.base]}" alt="${x.name}" loading="lazy"></div>`
      : '';
    return `<div class="card" style="--cc:${c}">
      ${bg}
      <div class="card-top">
        <div class="hd">${logo(x.brand)}
          <div class="nm">${x.name}<span class="en">${(x.brand?x.brand+' · ':'')+modelEn(x.name)}</span></div>
        </div>
        <div class="rk">${String(i+1).padStart(2,'0')}</div>
      </div>
      <div class="card-body">
        <div class="chips">
          <span class="chip b">${x.n} 次</span>
          ${vs.map(v=>`<span class="chip">${v}</span>`).join('')}
          <span class="chip">${x.stations.size} 个站点</span>
        </div>
        <div class="stats">
          <div class="stat"><div class="v">${hm(x.minutes)}</div><div class="k">总时长</div></div>
          <div class="stat"><div class="v">${fmt(x.km)}</div><div class="k">距离 km</div></div>
          <div class="stat"><div class="v">¥${fmt(x.yen)}</div><div class="k">金额 円</div></div>
        </div>
        <div class="bars">
          <div class="bar"><div class="t"><span>走行距離</span><b>${fmt(x.km)} km</b></div>
            <div class="track"><div class="fill" data-w="${(x.km/maxKm*100).toFixed(1)}%" style="background:linear-gradient(90deg,${c},${c}55)"></div></div></div>
          <div class="bar"><div class="t"><span>請求金額</span><b>¥${fmt(x.yen)}</b></div>
            <div class="track"><div class="fill" data-w="${(x.yen/maxYen*100).toFixed(1)}%" style="background:linear-gradient(90deg,${c}aa,${c})"></div></div></div>
        </div>
      </div>
      <div class="foot">
        <span>均次 <b>¥${fmt(Math.round(x.yen/x.n))}</b></span>
        <span>均次 <b>${(x.km/x.n).toFixed(1)} km</b></span>
        <span><b>¥${fmt(Math.round(x.yen/(x.minutes/60)))}</b>/時</span>
      </div>
    </div>`;
  }).join('');
  upgradeLogos($('#grid'));
  $('#grid').closest('.panel').classList.add('in');
  requestAnimationFrame(()=>$('#grid').querySelectorAll('.fill').forEach((f,i)=>setTimeout(()=>f.style.width=f.dataset.w,i*45)));
}

/* ---------- 对比图 ---------- */
const META = {km:['走行距離','km','#22d3ee'],yen:['請求金額','円','#ff3d81'],
  minutes:['利用時間','分','#facc15'],count:['利用回数','回','#a855f7']};
function renderChart(){
  const g = groupBy(MODE);
  const [label,unit,c] = META[METRIC];
  const arr = g.map(x=>({name:x.name,brand:x.brand,v:METRIC==='count'?x.n:x[METRIC]}))
               .sort((a,b)=>b.v-a.v);
  const max = Math.max(...arr.map(x=>x.v));
  $('#chart').innerHTML = arr.map((x,i)=>{
    const col = PALETTE[i%PALETTE.length];
    const show = METRIC==='minutes' ? hm(x.v) : fmt(x.v);
    return `<div class="crow">
      <div class="cn" title="${x.name}">${logo(x.brand,true)}<span>${x.name}</span></div>
      <div class="ctrack"><div class="cfill" data-w="${(x.v/max*100).toFixed(1)}%"
        style="background:linear-gradient(90deg,${col},${col}66)">${(x.v/max*100)>18?show:''}</div></div>
      <div class="cv"><b>${show}</b> ${unit}</div>
    </div>`;
  }).join('');
  upgradeLogos($('#chart'));
  requestAnimationFrame(()=>$('#chart').querySelectorAll('.cfill').forEach((f,i)=>setTimeout(()=>f.style.width=f.dataset.w,i*50)));
}
$('#metric').addEventListener('click',e=>{
  const b = e.target.closest('button'); if(!b) return;
  [...e.currentTarget.children].forEach(x=>x.classList.toggle('on',x===b));
  METRIC = b.dataset.k; renderChart();
});
$('#seg').addEventListener('click',e=>{
  const b = e.target.closest('button'); if(!b) return;
  [...e.currentTarget.children].forEach(x=>x.classList.toggle('on',x===b));
  MODE = b.dataset.m; renderCards(); renderChart();
});
$('#tint').addEventListener('click',e=>{
  const b = e.target.closest('button'); if(!b) return;
  [...e.currentTarget.children].forEach(x=>x.classList.toggle('on',x===b));
  TINT = b.dataset.t === '1';
  try{ localStorage.setItem('logo-tint', TINT ? '1' : '0'); }catch(err){}
  refreshLogos();
});

/* ---------- 月度 ---------- */
(function(){
  const m = new Map();
  R.forEach(r=>{const k=r.start.slice(0,7);
    if(!m.has(k)) m.set(k,{n:0,km:0,yen:0});
    const o=m.get(k); o.n++; o.km+=r.km; o.yen+=r.yen;});
  const ks=[...m.keys()].sort(), max=Math.max(...ks.map(k=>m.get(k).yen));
  $('#months').innerHTML = ks.map(k=>{
    const o=m.get(k), h=(o.yen/max*100);
    return `<div class="mcol">
      <div class="mbar" data-h="${Math.max(h,3)}%" style="height:0">
        <span>${o.n}次 · ${o.km}km · ¥${fmt(o.yen)}</span></div>
      <div class="mlb">${k.slice(5)}月</div></div>`;
  }).join('');
})();

/* ---------- 明细 ---------- */
let SORT='start', DESC=true;
function renderTable(){
  const q = $('#q').value.trim().toLowerCase();
  let rows = R.filter(r=>!q || (r.car+r.station+r.no+r.base).toLowerCase().includes(q));
  rows.sort((a,b)=>{
    const x=a[SORT], y=b[SORT];
    return (typeof x==='number' ? x-y : String(x).localeCompare(String(y))) * (DESC?-1:1);
  });
  $('#cnt').textContent = `${rows.length} / ${R.length} 条`;
  $('#tb').innerHTML = rows.map(r=>`
    <tr>
      <td class="mut">${r.start}</td>
      <td class="car"><span class="cw">${logo(r.brand,true)}${r.car}</span></td>
      <td>${r.station}</td>
      <td class="n">${hm(r.minutes)}</td>
      <td class="n">${r.km} km</td>
      <td class="n">¥${fmt(r.yen)}</td>
    </tr>`).join('') || `<tr><td colspan="6" style="text-align:center;color:#8b93ad;padding:30px">无匹配结果</td></tr>`;
  upgradeLogos($('#tb'));
}
$('#q').addEventListener('input',renderTable);
$('#sortseg').addEventListener('click',e=>{
  const b=e.target.closest('button'); if(!b) return;
  [...e.currentTarget.children].forEach(x=>x.classList.toggle('on',x===b));
  SORT=b.dataset.s; DESC=true; renderTable();
});
document.querySelectorAll('th[data-c]').forEach(th=>th.addEventListener('click',()=>{
  const c=th.dataset.c; DESC = (SORT===c) ? !DESC : true; SORT=c; renderTable();
}));

renderCards(); renderChart(); renderTable();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    sys.exit(main())
