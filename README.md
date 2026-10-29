# 玄奘译语词汇表（梵汉对勘）

比对玄奘译经论与现存梵本，编辛嶋式的全面词汇表；辅以真谛等旧译、唐代自注（光记、宝疏、玄应音义）和藏译（只用于无梵本的译本）。

## 成果

**离线资料包**：`成果/玄奘译语词汇表/`（文件夹）与 `成果/玄奘译语词汇表.zip`。解压后双击 `首页.html`，Windows、Mac 都能用，不需要联网、不需要安装软件；字体随包附带。包内有词汇表（含审定功能）、译经清单、表格资料和使用说明。

**审定**：在词汇表的"审定"页审定后导出 .json，放进 `审定/` 文件夹，用 `akbh1_apply_review.py` 应用（见 `审定/README.md`）。

## 数据的组织（为数据量扩大而设计）

- **工作数据（唯一的编辑对象）**：TSV 文本文件，按文本分目录（如 `_work/align/akbh1/occ/U01.tsv`），用 git 管理版本。子代理并行编写、审定套用、统一写法都改这里。
- **文本登记表** `_work/align/texts.tsv`：每部文本一行（编号、大正藏号、所在册、梵本来源、对照的旧译、数据目录）。网页和数据库都从这里取文本信息；新增文本先在这里登记。
- **规范词目表** `_work/align/lemmas.tsv`：全书共用，每个词目只有一种标准写法，附词类、出现次数、主要译法、异写。体例自查对照它：异写报错，未登记的新词目提示登记。新数据写完后运行 `akbh1_lemmas.py align` 登记新词目，确认写法后把状态改为"已登记"。
- **SQLite 查询库**：每次打包时由 TSV 生成（`表格/玄奘译语.sqlite`），含存档的全部虚词例句，供跨文本检查、统计和研究查询；不在上面编辑。
- **网页资料包**：由 TSV 生成，供阅读、分享、审定。

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
python3 -I scripts/akbh1_lint.py align/akbh1/occ/U*.tsv  # 体例自查（译语切分、形态格式、末成分与复合词一致、性与词尾）
python3 -I scripts/akbh1_normalize.py align/akbh1      # 统一写法（合并多批数据后；含形态次序）
python3 -I scripts/akbh1_morph_todo.py align/akbh1 U06  # 列出形态未标全的记录（附末成分关系、梵文句）
python3 -I scripts/akbh1_morph_apply.py align/akbh1 MAP.tsv --dry   # 按对照表（oid、pos）改形态，先核验格式
python3 -I scripts/akbh1_cpd_todo.py align/akbh1 U06 > todo.json  # 找缺整词记录的复合词（有误报，逐个判断）
python3 -I scripts/akbh1_add_records.py align/akbh1 NEW.tsv --dry   # 新增记录：自动编号，核验后插入
python3 -I scripts/akbh1_edit_records.py align/akbh1 EDITS.tsv --dry # 改已有记录的 skt、lemma、pos、note
python3 -I scripts/akbh1_lemmas.py align               # 更新规范词目表（新词目记为"新增"，待确认）
python3 -I scripts/akbh1_prune.py align/akbh1          # 虚词、语法形式每种对应只留两例，多出的存档
python3 -I scripts/akbh1_glossary.py align/akbh1 ../试点-俱舍界品 align/akbh1/tangnotes.tsv
python3 -I scripts/akbh1_review.py align/akbh1 ../试点-俱舍界品/待核清单.md
python3 -I scripts/akbh1_calib.py src/eduhk align/akbh1 "$(cat align/akbh1/eduhk_pagemap.txt)" align/akbh1/calib_eduhk_full.tsv

python3 -I scripts/build_sqlite.py align ../清单/玄奘译经清单.csv 某处/玄奘译语.sqlite   # 单独生成查询库（打包时会自动生成）

# 离线资料包（词汇表、清单、表格、SQLite、字体子集、zip）；需要 _work/.venv 中的 fontTools、brotli
cd .. && _work/.venv/bin/python _work/scripts/pkg_build.py
```

资料包的词汇表页面由外壳（`词汇表.html`）和数据（`data/akbh1.js`，句子与语境去重存放）组成，数据用 `<script>` 载入，本地双击也能读取；以后增加的品各自一个数据文件。字体由 `pkg_fonts.py` 按包内实际用字从 Noto Serif SC/TC、Noto Sans SC 抽取子集；Gentium Book Plus 有保留字体名，按 OFL 原样附带。审定结果保存在浏览器的 localStorage 里，导出为 .json 交回。

形态标注（pos 栏）的格式规则在 `_work/scripts/morph.py`：名词类按词类、性、数、格，动词按时态/语气、语态、人称数；复合词末成分照整个复合词标。`align/akbh1/units_map.tsv`（玄奘颂块与梵本、真谛起点的对应）是人工指定的。U06–U54 由七批子代理并行编写，各批汇报的疑点记在 `align/akbh1/batch_reports.md`，整理后的梵本问题在 `align/akbh1/review_notes.md`。各 HTML 页面共用 `_work/scripts/page_style.py` 里的字体与配色（Noto Serif SC/TC、Gentium Book Plus）；资料包里用随包字体，`清单/` 下的单页版从 Google Fonts 加载。词类、语法标注的缩略语说明在 `_work/scripts/abbr.py`，词汇表的"缩略语"页和悬停提示都由它生成；生成时如果遇到说明表里没有的写法会提示补充。`src/` 下是下载的语料，作不可信数据处理，只当文本读。

## 版本管理

项目是 git 仓库。下载的原始语料（`_work/src/`）、Python 环境（`_work/.venv/`）和生成的资料包（`成果/`）不纳入版本管理：语料可按"语料来源"重新下载，资料包随时可重建。

## 语料来源

CBETA xml-p5（GitHub cbeta-org）、CBETA API（cbdata.dila.edu.tw）、GRETIL、Lancaster *The Korean Buddhist Canon: A Descriptive Catalogue*（acmuller.net）、香港教育大学梵汉对勘语料库（仅用于本地校准）。
