# -*- coding: utf-8 -*-
"""
gen_script.py —— 把 Merge 格式的规则转换成 Clash Verge 全局脚本 Script.js

用法（方法一：Merge 转换）：
  1. 编辑本目录的 ClashVerge-Merge.yaml（保持 prepend-rules: 结构不变），
     或在 Clash Verge 的全局扩展 Merge 里编辑后把内容同步回来；
  2. 运行本脚本：python gen_script.py
  3. 打开 Clash Verge → 设置 → 全局扩展 → 脚本(Script) → 编辑
  4. 把生成的 Script.js 内容全选替换进编辑器，保存
  5. 回到订阅列表点「重新订阅」生效

方法二（直接写 JS）：
  不用本脚本，直接在 Clash Verge 全局脚本编辑器里改 DIRECT_RULES 数组，
  加一行即可，例如：  "DOMAIN-SUFFIX,xxx.com,DIRECT",

背景：Merge 扩展的 prepend-rules 在 mihomo 核心中不生效（被静默忽略，
      详见 README「踩过的坑」），真正生效的是 Script 扩展的 main(config)，
      本脚本只负责把 Merge 格式转成 JS 格式。
"""
import io
import os

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, "ClashVerge-Merge.yaml")  # 规则源（Merge 格式）
DST = os.path.join(BASE, "Script.js")              # 输出（全局脚本内容）

with io.open(SRC, encoding="utf-8") as f:
    lines = f.read().splitlines()

# 提取 prepend-rules: 块下的所有规则行
rules = []
in_block = False
for ln in lines:
    stripped = ln.strip()
    if stripped == "prepend-rules:":
        in_block = True
        continue
    if in_block:
        if ln.startswith("  - "):
            item = ln[4:].split("#")[0].strip()
            if item:
                rules.append(item)
        elif stripped and not stripped.startswith("#"):
            break  # 到了下一个顶层键

# 去重（保持顺序）
seen = set()
final = []
for r in rules:
    if r not in seen:
        seen.add(r)
        final.append(r)

js = """// ============================================================
// 国内直连规则（全局生效，套用于所有订阅）
// 本文件由 gen_script.py 从 ClashVerge-Merge.yaml 自动生成
// 用法：粘贴到 Clash Verge → 设置 → 全局扩展 → 脚本(Script) → 编辑
// 也可以直接在此文件里增删规则行（方法二），改完重新订阅即可
// ============================================================

const DIRECT_RULES = [
""" + "".join('  "%s",\n' % r for r in final) + """];

function main(config, profileName) {
  if (!Array.isArray(config.rules)) config.rules = [];
  config.rules = DIRECT_RULES.concat(config.rules);
  return config;
}
"""

os.makedirs(os.path.dirname(DST), exist_ok=True)
with io.open(DST, "w", encoding="utf-8", newline="\n") as f:
    f.write(js)

print("生成成功: %s" % DST)
print("规则数量: %d 条" % len(final))
