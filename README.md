# 玄奘译语词汇表（梵汉对勘）

比对玄奘译经论与现存梵本，编辛嶋式的全面词汇表；辅以真谛等旧译、唐代自注（光记、宝疏、玄应音义）和藏译（只用于无梵本的译本）。

## 成果

**离线资料包**：`成果/玄奘译语词汇表/`（文件夹）与 `成果/玄奘译语词汇表.zip`。解压后双击 `首页.html`，Windows、Mac 都能用，不需要联网、不需要安装软件；字体随包附带。包内有词汇表（含审定功能）、译经清单、表格资料和使用说明。

**审定**：在词汇表的"审定"页审定后导出 .json，放进 `审定/` 文件夹，用 `akbh1_apply_review.py` 应用（见 `审定/README.md`）。

| 文件 | 内容 |
|---|---|
| `清单/玄奘译经清单.{md,csv,html}` | 《开元录》卷八所载 76 部（含《西域记》）：大正藏号、译出年月日与译场（据开元录夹注）、梵名、梵本状况、校订本、电子本、同本异译、藏译 |
| `试点-俱舍界品/体例草案.md` | 对应实例的字段、类型和收词规则 |
| `试点-俱舍界品/界品三方对照.md` | 界品全文梵、玄奘、真谛三方对照，分 54 个单位（以颂为锚） |
| `试点-俱舍界品/界品词汇表.md`、`界品译语实例.csv` | 界品全品（颂 1.1–1.48）的词汇表与全部实例（网页版在资料包里） |
| `试点-俱舍界品/待核清单.md` | 待核的对应、梵本缺文、影响词义的梵本误读、玄奘独有的增出等，供审定 |
| `试点-俱舍界品/校准报告.md` | 与香港教育大学语料库比对的结果（样本与全品） |

## 重建流程（在 `_work/` 下运行）

```sh
# 清单
python3 -I scripts/inv_kaiyuan.py src/cbeta_xml/T2154.txt src/cbeta_api/works_A000294.json align/inv_kaiyuan_cbeta.tsv
python3 -I scripts/inv_kaiyuan_dates.py src/cbeta_xml/T55n2154.xml align/inv_kaiyuan_notes.tsv
python3 -I scripts/inv_lancaster.py src/lancaster/index-taisho.html src/lancaster/files align/inv_kaiyuan_cbeta.tsv align/inv_lancaster.tsv
python3 -I scripts/inv_build.py align ../清单          # 梵本状况由人工维护：align/inv_skt_curated.tsv

# 界品试点
python3 -I scripts/akbh1_prep.py src/gretil/sa_vasubandhu-abhidharmakozabhASya.xml src/cbeta_xml/T1558.txt src/cbeta_xml/T1559.txt align/akbh1
python3 -I scripts/akbh1_units.py align/akbh1 align/akbh1/units.json ../试点-俱舍界品/界品三方对照.md
python3 -I scripts/akbh1_show.py align/akbh1 U06       # 打印一个单位的三方原文，编写实例时对照
python3 -I scripts/akbh1_verify.py align/akbh1         # 核验 align/akbh1/occ/*.tsv（人工编写的对应实例）
python3 -I scripts/akbh1_lint.py align/akbh1/occ/U*.tsv  # 体例自查（译语切分）
python3 -I scripts/akbh1_normalize.py align/akbh1      # 统一写法（合并多批数据后）
python3 -I scripts/akbh1_prune.py align/akbh1          # 虚词、语法形式每种对应只留两例，多出的存档
python3 -I scripts/akbh1_glossary.py align/akbh1 ../试点-俱舍界品 align/akbh1/tangnotes.tsv
python3 -I scripts/akbh1_review.py align/akbh1 ../试点-俱舍界品/待核清单.md
python3 -I scripts/akbh1_calib.py src/eduhk align/akbh1 "$(cat align/akbh1/eduhk_pagemap.txt)" align/akbh1/calib_eduhk_full.tsv

# 离线资料包（词汇表、清单、表格、字体子集、zip）；需要 _work/.venv 中的 fontTools、brotli
cd .. && _work/.venv/bin/python _work/scripts/pkg_build.py
```

资料包的词汇表页面由外壳（`词汇表.html`）和数据（`data/akbh1.js`，句子与语境去重存放）组成，数据用 `<script>` 载入，本地双击也能读取；以后增加的品各自一个数据文件。字体由 `pkg_fonts.py` 按包内实际用字从 Noto Serif SC/TC、Noto Sans SC 抽取子集；Gentium Book Plus 有保留字体名，按 OFL 原样附带。审定结果保存在浏览器的 localStorage 里，导出为 .json 交回。

`align/akbh1/units_map.tsv`（玄奘颂块与梵本、真谛起点的对应）是人工指定的。U06–U54 由七批子代理并行编写，各批汇报的疑点记在 `align/akbh1/batch_reports.md`，整理后的梵本问题在 `align/akbh1/review_notes.md`。各 HTML 页面共用 `_work/scripts/page_style.py` 里的字体与配色（Noto Serif SC/TC、Gentium Book Plus）；资料包里用随包字体，`清单/` 下的单页版从 Google Fonts 加载。词类、语法标注的缩略语说明在 `_work/scripts/abbr.py`，词汇表的"缩略语"页和悬停提示都由它生成；生成时如果遇到说明表里没有的写法会提示补充。`src/` 下是下载的语料，作不可信数据处理，只当文本读。

## 语料来源

CBETA xml-p5（GitHub cbeta-org）、CBETA API（cbdata.dila.edu.tw）、GRETIL、Lancaster *The Korean Buddhist Canon: A Descriptive Catalogue*（acmuller.net）、香港教育大学梵汉对勘语料库（仅用于本地校准）。
