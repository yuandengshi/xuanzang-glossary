"""抽出报告中的 CBETA 行号，打印该行及下一行文字，供逐条核对引文。

用法：python3 -I verify_ids.py <report.md> <cbeta_txt_dir>[,<另一目录>...]
行号格式涵盖大正藏、卍续藏及嘉兴藏、补编、高丽藏、永乐北藏、太虚、演培等其他部类。
"""
import os
import re
import sys

report, dirs = sys.argv[1], sys.argv[2].split(",")
text = open(report, encoding="utf-8").read()
ids = sorted(set(re.findall(r"\b([A-Z]{1,2}\d{2,3}n[A-Z]?\d{3,4}[a-zA-Z]?_p[a-z]?\d{3,4}[abc]\d\d)\b", text)))
cache = {}
for lid in ids:
    work = lid.split("_p")[0]
    if work not in cache:
        path = next((os.path.join(d, work + ".txt") for d in dirs if os.path.exists(os.path.join(d, work + ".txt"))), None)
        lines = open(path, encoding="utf-8").read().split("\n") if path else []
        cache[work] = ([l.split("\t")[0] for l in lines], [l.split("\t")[-1] for l in lines])
    keys, vals = cache[work]
    if lid in keys:
        i = keys.index(lid)
        print(f"{lid}\t{vals[i]}{vals[i + 1] if i + 1 < len(vals) else ''}")
    else:
        print(f"{lid}\t!!! 行号不存在")
