#!/usr/bin/env python3
"""pkg_build.py -- 生成离线资料包（Windows、Mac 双击即用，无需联网、无需安装软件）。

Usage: _work/.venv/bin/python _work/scripts/pkg_build.py
  （在 xuanzang-glossary 项目目录下运行；需要 _work/.venv 中的 fontTools、brotli）
输出：成果/玄奘译语词汇表/（文件夹）与 成果/玄奘译语词汇表.zip
包内：首页.html、词汇表.html、译经清单.html、data/、fonts/、表格/、使用说明.txt
"""
import datetime
import os
import shutil
import subprocess
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import page_style  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
W = os.path.join(ROOT, '_work')
PKG = os.path.join(ROOT, '成果', '玄奘译语词汇表')
ZIP = PKG + '.zip'


def run(*args):
    print('$', ' '.join(args[1:]))
    subprocess.run(['python3', '-I'] + list(args[1:]), check=True, cwd=W)


HOME = '''<!doctype html>
<html lang="zh-Hans"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>玄奘译语词汇表</title>
{fonts}
<style>{base}
main{{max-width:980px}}
.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:14px;margin:26px 0}}
.card{{display:block;background:var(--paper);border:1px solid var(--line);border-radius:14px;padding:18px 20px;color:var(--ink);text-decoration:none}}
.card:hover{{border-color:var(--acc);text-decoration:none}}
.card h2{{font:700 20px/1.4 var(--zh);margin:0 0 6px;color:var(--acc)}}
.card p{{margin:0;font-family:var(--zh);font-size:15px;color:var(--mut);line-height:1.8}}
.card .n{{font-family:var(--sans);font-size:12.5px;color:var(--mut);margin-top:10px}}
h3{{font:700 17px/1.4 var(--zh);margin:28px 0 8px}}
ul{{font-family:var(--zh);font-size:15.5px;line-height:1.9;padding-left:1.3em;margin:0}}
.foot{{margin-top:36px;font-family:var(--sans);font-size:12.5px;color:var(--mut);line-height:1.8}}
</style></head><body><main>
<header class="top"><p class="kicker">玄奘译语词汇表 · 离线资料包</p><h1>玄奘译语词汇表</h1>
<p class="lead">对勘玄奘译经论与现存梵本，逐词记录玄奘的译法，附真谛旧译与唐代注疏的自注。目前收录俱舍论·界品全品。全部资料都在本文件夹内，不需要联网，也不需要安装任何软件。</p></header>
<div class="cards">
<a class="card" href="词汇表.html"><h2>词汇表 · 俱舍论界品</h2><p>梵→汉词条、语法形式、汉→梵反查、增译与省译、缩略语；每条附梵汉原句与出处。可在"审定"页逐条审定。</p><div class="n">{n_occ} 条对应 · {n_lem} 个梵文词目</div></a>
<a class="card" href="译经清单.html"><h2>玄奘译经清单</h2><p>《开元录》所载玄奘所出 76 部：译出年月、译场、梵名、梵本存世状况、校订本、同本异译、藏译。</p><div class="n">76 部 · 1347 卷</div></a>
</div>
<h3>使用</h3>
<ul>
<li>请保持文件夹完整：页面要和 data、fonts 两个文件夹放在一起，不要单独拿出某个 .html 文件。</li>
<li>用 Chrome、Edge、Safari、Firefox 打开都可以。大正藏出处链接到 CBETA 网站，只有这一项需要联网。</li>
<li>审定：在词汇表的"审定"页（或任何例句下的"审定"按钮）选择"同意、改正、存疑"。结果自动保存在当前浏览器里；审完请点"导出审定结果"，把得到的 .json 文件交给编者。</li>
<li>"表格"文件夹里有全部对应实例（CSV，可用 Excel、Numbers 打开）、译经清单（CSV）和待核清单（Markdown）。</li>
<li>需要自己做统计或复杂查询的，可以用免费的 DB Browser for SQLite 打开"表格"里的 玄奘译语.sqlite（含词汇表未收的全部虚词例句），查询示例.sql 里有常用写法。</li>
</ul>
<p class="foot">生成于 {date}。字体：Noto Serif SC、Noto Serif TC、Noto Sans SC（按所用字抽取的子集）与 Gentium Book Plus，均依 SIL Open Font License 1.1 随包分发，许可证见 fonts 文件夹。梵本据 GRETIL 所收 Pradhan 本；汉文据 CBETA。</p>
</main></body></html>
'''

GUIDE = '''玄奘译语词汇表 · 离线资料包  使用说明
=====================================

一、打开
  解压后，双击文件夹里的"首页.html"。Windows、Mac 都可以，用 Chrome、Edge、Safari、Firefox 打开均可。
  不需要联网，也不需要安装任何软件。

  注意：请保持文件夹完整。页面要和 data、fonts 两个文件夹放在一起，不要单独拿出某个 .html 文件。

二、内容
  首页.html      入口
  词汇表.html    俱舍论·界品的玄奘译语词汇表（梵→汉、语法形式、汉→梵、增译省译、缩略语、审定）
  译经清单.html  《开元录》所载玄奘所出 76 部的清单
  表格\\          对应实例（CSV）、译经清单（CSV）、待核清单（Markdown）。CSV 可用 Excel、Numbers 打开。
                 玄奘译语.sqlite：全部数据的数据库（含词汇表未收的全部虚词例句），
                 可用免费的 DB Browser for SQLite（sqlitebrowser.org）打开；查询示例.sql 里有常用写法。
  data\\  fonts\\  页面用到的数据和字体，请勿删除

三、审定
  1. 打开词汇表，点上方的"审定"。这里列出所有标"待核"的条目和梵本缺文；其他任何例句下面也有"审定"按钮。
  2. 填上"审定人"，逐条选择"同意""改正""存疑"。选"改正"时可以直接改词目、译语、类型，并写说明。
  3. 结果会自动保存在当前浏览器里，关掉再打开还在。
     但换一个浏览器、使用隐私模式或清除浏览器数据后就看不到了，所以请记得导出。
  4. 审完（或中途）点"导出审定结果"，会下载一个 .json 文件，把它交给编者即可。
  5. 换电脑或换浏览器继续审：点"导入"，选之前导出的 .json 文件。

四、其他
  大正藏出处（如 T29.1a09）链接到 CBETA 网站，只有这一项需要联网。
  字体依 SIL Open Font License 1.1 随包分发，许可证见 fonts 文件夹。

生成日期：{date}
'''


QUERIES = '''-- 玄奘译语.sqlite 查询示例（可在 DB Browser for SQLite 的"执行 SQL"页运行）
-- 各表、各字段的说明见表 _说明。

-- 1. 某个梵文词目的全部译法及次数（含存档例句）
SELECT xz, type, n, archived_n FROM v_renderings WHERE lemma = 'kleśa' ORDER BY n DESC;

-- 2. 某个梵文词目的全部例句，连同梵文句和玄奘原行
SELECT oid, pradhan, skt_sentence, xz, xz_line, xz_line_text FROM v_records WHERE lemma = 'pratisaṃkhyā-nirodha';

-- 3. 汉→梵：玄奘用某个汉语译语对应了哪些梵文词
SELECT lemma, type, COUNT(*) AS n FROM records WHERE xz = '相' GROUP BY lemma, type ORDER BY n DESC;

-- 4. 语法形式：第五格（abl.）玄奘的各种处理
SELECT xz, n, archived_n FROM v_renderings WHERE lemma = 'abl.' ORDER BY n DESC;

-- 5. 玄奘与真谛对同一梵文词的译法对照
SELECT lemma, xz AS 玄奘, pm AS 真谛, COUNT(*) AS n FROM records
 WHERE pm != '' AND type NOT IN ('增译', '梵本缺文') GROUP BY lemma, xz, pm ORDER BY lemma;

-- 6. 各单位的增译数
SELECT unit, COUNT(*) AS n FROM records WHERE type = '增译' GROUP BY unit ORDER BY n DESC;

-- 7. 待核与梵本缺文
SELECT oid, lemma, skt, xz, type, note FROM records WHERE note LIKE '%待核%' OR type = '梵本缺文';

-- 8. 词目表：出现最多的 50 个实词词目
SELECT lemma, class, count, renderings FROM lemmas WHERE class NOT LIKE 'gram.%' ORDER BY count DESC LIMIT 50;
'''


def main():
    if os.path.exists(PKG):
        shutil.rmtree(PKG)
    os.makedirs(os.path.join(PKG, '表格'))
    run('python3', 'scripts/akbh1_lemmas.py', 'align')
    run('python3', 'scripts/akbh1_glossary.py', 'align/akbh1', '../试点-俱舍界品', 'align/akbh1/tangnotes.tsv', '--pkg=' + PKG)
    run('python3', 'scripts/inv_build.py', 'align', '../清单', PKG)
    run('python3', 'scripts/akbh1_review.py', 'align/akbh1', '../试点-俱舍界品/待核清单.md')
    for src, dst in [('试点-俱舍界品/界品译语实例.csv', '俱舍论界品-对应实例.csv'),
                     ('清单/玄奘译经清单.csv', '玄奘译经清单.csv'),
                     ('试点-俱舍界品/待核清单.md', '俱舍论界品-待核清单.md'),
                     ('试点-俱舍界品/体例草案.md', '体例说明.md')]:
        shutil.copy(os.path.join(ROOT, src), os.path.join(PKG, '表格', dst))
    run('python3', 'scripts/build_sqlite.py', 'align', '../清单/玄奘译经清单.csv', os.path.join(PKG, '表格', '玄奘译语.sqlite'))
    open(os.path.join(PKG, '表格', '查询示例.sql'), 'w', encoding='utf-8').write(QUERIES)
    n_occ = sum(1 for _ in open(os.path.join(ROOT, '试点-俱舍界品/界品译语实例.csv'), encoding='utf-8-sig')) - 1
    import csv
    n_lem = len({r['lemma'] for r in csv.DictReader(open(os.path.join(ROOT, '试点-俱舍界品/界品译语实例.csv'), encoding='utf-8-sig'))
                 if r['lemma'] and not r['pos'].startswith('gram')})
    date = datetime.date.today().isoformat()
    open(os.path.join(PKG, '首页.html'), 'w', encoding='utf-8').write(
        HOME.format(fonts=page_style.LOCAL_FONT_LINK, base=page_style.BASE_CSS, n_occ=n_occ, n_lem=n_lem, date=date))
    with open(os.path.join(PKG, '使用说明.txt'), 'w', encoding='utf-8-sig', newline='\r\n') as f:
        f.write(GUIDE.format(date=date))
    print('$ pkg_fonts.py')
    subprocess.run([sys.executable, '-I', os.path.join(HERE, 'pkg_fonts.py'), os.path.join(W, 'src', 'fonts'), PKG], check=True)
    if os.path.exists(ZIP):
        os.remove(ZIP)
    with zipfile.ZipFile(ZIP, 'w', zipfile.ZIP_DEFLATED) as z:
        for base, _, files in os.walk(PKG):
            for fn in sorted(files):
                full = os.path.join(base, fn)
                z.write(full, os.path.relpath(full, os.path.dirname(PKG)))
    size = lambda p: sum(os.path.getsize(os.path.join(b, f)) for b, _, fs in os.walk(p) for f in fs)
    print('资料包 %.1f MB；zip %.1f MB' % (size(PKG) / 1e6, os.path.getsize(ZIP) / 1e6))


if __name__ == '__main__':
    main()
