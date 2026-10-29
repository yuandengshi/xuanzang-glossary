#!/usr/bin/env python3
"""inv_build.py -- 合并开元录夹注、CBETA、Lancaster、人工整理的梵本信息，生成《玄奘译经清单》。

Usage: python3 -I inv_build.py ALIGN_DIR OUT_DIR
  读取 ALIGN_DIR 下 inv_kaiyuan_notes.tsv、inv_kaiyuan_cbeta.tsv、inv_lancaster.tsv、inv_skt_curated.tsv
  输出 OUT_DIR/玄奘译经清单.csv、.md、.html
"""
import csv
import html
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # 同目录的 page_style（-I 模式下不自动加入）
import page_style  # noqa: E402

ERA = '(?:貞觀|永徽|顯慶|龍朔|麟德)'
STATUS_ORDER = ['完整', '大部', '部分', '残片', '无', '待核', '非翻译']


def tsv(path):
    with open(path, encoding='utf-8') as f:
        return list(csv.DictReader(f, delimiter='\t', restval=''))


def status_key(s):
    for i, k in enumerate(STATUS_ORDER):
        if s.startswith(k):
            return k
    return '梵本存世' if s.startswith('梵本存世') else s


def parse_note(n):
    d = {}
    m = re.search(r'(%s[元一二三四五六七八九十]+年.*?)(?=於|奉勅)' % ERA, n)
    d['时间'] = m.group(1) if m else ''
    rest = n[m.start():] if m else n
    m2 = re.search(r'至(.+?)畢', rest)
    if m2:
        d['时间'] += '—' + m2.group(1).split('於')[0]
    m3 = re.search(r'於(.+?)(?:翻經院)?譯', rest)
    d['译场'] = m3.group(1) if m3 else ''
    m = re.search(r'與(.+?)並?同本', n)
    d['开元录同本'] = m.group(1) if m else ''
    m = re.search(r'沙門(.+?)筆受', n)
    d['笔受'] = m.group(1) if m else ''
    return d


def main(adir, odir, pkg=None):
    notes = {r['序']: r for r in tsv(os.path.join(adir, 'inv_kaiyuan_notes.tsv'))}
    notes.setdefault('76', {'序': '76', '出處': 'T55.0557b11', '題名': '大唐西域記', '卷': '十二卷',
                            '夾注': '見內典錄貞觀二十年奉勅於弘福寺翻經院撰沙門辯機承旨綴緝秋七月絕筆'})
    cb = {r['開元錄序']: r for r in tsv(os.path.join(adir, 'inv_kaiyuan_cbeta.tsv')) if r['開元錄序']}
    lan = {}
    for r in tsv(os.path.join(adir, 'inv_lancaster.tsv')):
        lan.setdefault(r['T'], r)
    lan['K0016'] = lan.get('T220-09', {})
    cur = {r['序']: r for r in tsv(os.path.join(adir, 'inv_skt_curated.tsv'))}
    api = {w['work']: w for w in json.load(open(os.path.join(adir, '..', 'src', 'cbeta_api', 'works_A000294.json'),
                                                encoding='utf-8'))['results']}
    rows = []
    for k in sorted(cur, key=int):
        c, n = cur[k], notes[k]
        b = cb.get(k, {})
        t = c['T']
        tkey = t if t.startswith('K') else 'T' + t[1:].lstrip('0')
        l = lan.get(tkey, {})
        pn = parse_note(n['夾注'])
        w = api.get(t if not t[1:].isdigit() else t[0] + t[1:].zfill(4), {})
        year = era_years(pn['时间'])
        cby = (w.get('time_from'), w.get('time_to'))
        note_cb = ''
        if year and cby[0] and cby[1] - cby[0] < 50:
            ys = [int(y) for y in re.findall(r'[0-9]{3}', year)]
            if abs(ys[0] - cby[0]) > 1 or abs(ys[-1] - cby[1]) > 1:
                note_cb = 'CBETA 记作 %s–%s，与开元录不合' % cby
        rows.append({
            '序': k, '题名': n['題名'], '卷': b.get('開元錄卷') or n['卷'], '大正藏号': t,
            '译出时间（开元录）': pn['时间'], '公元': year, '译场': pn['译场'], '笔受': pn['笔受'],
            '梵名（Lancaster）': l.get('梵名', ''), '梵名异称': l.get('梵名异称', ''),
            '梵本状况': c['梵本状况'], '状况类': status_key(c['梵本状况']),
            '梵本校订本': c['梵本校订本'], '电子本': c['电子本'],
            '同本异译': c['同本异译'], '开元录同本记载': pn['开元录同本'],
            '藏译': c['藏译'] or ('To.' + l['Tohoku'] if l.get('Tohoku') else ''),
            '备注': '；'.join(x for x in (c['备注'], note_cb) if x), '开元录出处': n['出處'], '开元录夹注': n['夾注'],
            'Lancaster': l.get('URL', ''),
        })
    for r in rows:
        r['卷'] = str(cn(r['卷'])) if not r['卷'].isdigit() else r['卷']
    os.makedirs(odir, exist_ok=True)
    cols = list(rows[0].keys())
    with open(os.path.join(odir, '玄奘译经清单.csv'), 'w', encoding='utf-8-sig', newline='') as f:
        wr = csv.DictWriter(f, fieldnames=cols)
        wr.writeheader()
        wr.writerows(rows)
    stats = summarize(rows)
    write_md(rows, stats, os.path.join(odir, '玄奘译经清单.md'))
    write_html(rows, stats, cols, os.path.join(odir, '玄奘译经清单.html'))
    if pkg:  # 离线资料包：同一页面，字体改用包内文件
        write_html(rows, stats, cols, os.path.join(pkg, '译经清单.html'), local=True)
    for s in stats:
        print(s)


LEGEND = [('T220', '大正新修大藏经编号；T310-12 指 T310《大宝积经》第十二会'), ('K0016', 'CBETA 所收高丽藏编号（648 年单译的《能断金刚经》）'), ('To.16', '德格版藏文大藏经《东北目录》编号'), ('梵名', '据 Lancaster《高丽大藏经解题目录》，点击可到该条目；经核查有误的已在备注中注明'), ('公元', '据《开元录》夹注所记年号换算，只算年份，不细算月日'), ('同本异译', '后出的译本注"后出"；"部分"指只有部分内容相当'), ('部 · 卷', '状况筛选按钮上的部数与卷数合计')]

ERA_BASE = {'貞觀': 626, '永徽': 649, '顯慶': 655, '龍朔': 660, '麟德': 663}


def era_years(t):
    """开元录夹注的年号纪年 → 公元年（按年号年数换算，不细算月日）；省略年号的沿用前一年号。"""
    ys, era = [], None
    for e, n in re.findall(r'(貞觀|永徽|顯慶|龍朔|麟德)?([元一二三四五六七八九十]+)年', t):
        era = e or era
        if era:
            ys.append(ERA_BASE[era] + (1 if n == '元' else cn(n)))
    if not ys:
        return ''
    return str(ys[0]) if ys[0] == ys[-1] else '%d–%d' % (ys[0], ys[-1])


def cn(s):
    m = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9}
    s = s.replace('卷', '')
    n = cur = 0
    for ch in s:
        if ch in m:
            cur = m[ch]
        elif ch == '十':
            n += (cur or 1) * 10; cur = 0
        elif ch == '百':
            n += (cur or 1) * 100; cur = 0
    return n + cur


def summarize(rows):
    out = []
    for k in STATUS_ORDER + ['梵本存世']:
        rs = [r for r in rows if r['状况类'] == k]
        if rs:
            out.append((k, len(rs), sum(int(r['卷']) for r in rs)))
    return out


def write_md(rows, stats, path):
    L = ['# 玄奘译经清单', '',
         '依据：《开元释教录》卷八（T2154，T55.555b–557b）著录玄奘所出"七十六部一千三百四十七卷"。'
         '去掉《大唐西域记》十二卷，翻译为 75 部 1335 卷。'
         'CBETA 编号、梵名、藏译分别取自 CBETA API（cbdata.dila.edu.tw）和 Lancaster《高丽大藏经解题目录》。'
         '梵本状况为人工整理，标"待核"的条目尚未查实。', '',
         '## 按梵本状况统计', '', '| 梵本状况 | 部数 | 卷数 |', '|---|---:|---:|']
    for k, n, j in stats:
        L.append('| %s | %d | %d |' % (k, n, j))
    L += ['', '注：《大般若》（600 卷）算作"部分"，但只有其中几会有梵本，见备注。', '',
          '## 清单', '', '| 序 | 题名 | 卷 | 大正藏 | 公元 | 梵名 | 梵本状况 | 同本异译 |', '|---:|---|---:|---|---|---|---|---|']
    for r in rows:
        L.append('| %s | %s | %s | %s | %s | %s | %s | %s |' % (
            r['序'], r['题名'], r['卷'], r['大正藏号'], r['公元'], r['梵名（Lancaster）'] or '—',
            r['梵本状况'], r['同本异译'] if r['同本异译'] not in ('', '—') else '—'))
    L += ['', '## 编号与缩略语', '', '| 写法 | 说明 |', '|---|---|'] + ['| %s | %s |' % x for x in LEGEND]
    L += ['', '## 有梵本可对勘的译本（完整、大部、部分）', '']
    for r in rows:
        if r['状况类'] in ('完整', '大部', '部分'):
            L.append('- **%s**（%s，%s 卷）：%s。电子本：%s。%s' % (
                r['题名'], r['大正藏号'], r['卷'], r['梵本校订本'], r['电子本'] or '—', r['备注']))
    open(path, 'w', encoding='utf-8').write('\n'.join(L) + '\n')


def write_html(rows, stats, cols, path, local=False):
    """主表只列八项；其余（校订本、电子本、同本异译、藏译、备注、开元录夹注）点行展开。"""
    show = ['序', '题名', '卷', '大正藏号', '公元', '译场', '梵名（Lancaster）', '梵本状况']
    detail = ['梵名异称', '梵本校订本', '电子本', '同本异译', '开元录同本记载', '藏译', '备注', '译出时间（开元录）', '开元录夹注']
    heads = {'梵名（Lancaster）': '梵名', '大正藏号': '大正藏'}
    dlab = {'开元录同本记载': '开元录"同本"', '译出时间（开元录）': '译出时间', '开元录夹注': '开元录夹注'}

    def cell(r, c):
        v = html.escape(r[c])
        if c == '大正藏号' and re.match(r'[TK][0-9]', r[c]):
            work = re.sub(r'-.*', '', r[c])
            work = work[0] + work[1:].zfill(4)
            v = '<a href="https://cbetaonline.dila.edu.tw/zh/%s" target="_blank" rel="noopener">%s</a>' % (work, v)
        if c == '梵名（Lancaster）':
            v = v or '—'
            if r['Lancaster']:
                v = '<a href="%s" target="_blank" rel="noopener">%s</a>' % (html.escape(r['Lancaster']), v)
        if c == '梵本状况':
            v = '<span class="dot s-%s"></span>%s' % (html.escape(r['状况类']), v)
        return v
    trs = []
    for r in rows:
        trs.append('<tr class="m" data-s="%s">%s<td class="c-x">▾</td></tr>' % (
            html.escape(r['状况类']), ''.join('<td class="c-%d">%s</td>' % (i, cell(r, c)) for i, c in enumerate(show))))
        dl = ''.join('<div><dt>%s</dt><dd>%s</dd></div>' % (dlab.get(c, c), html.escape(r[c]))
                     for c in detail if r[c] and r[c] != '—')
        trs.append('<tr class="d"><td colspan="%d"><dl>%s</dl></td></tr>' % (len(show) + 1, dl))
    chips = ''.join('<button class="chip" data-f="%s"><span class="dot s-%s"></span>%s<b>%d</b><i>部 · %d 卷</i></button>'
                    % (k, k, k, n, j) for k, n, j in stats)
    legend = ''.join('<div><dt>%s</dt><dd>%s</dd></div>' % (html.escape(a), html.escape(b)) for a, b in LEGEND)
    page = (TEMPLATE.replace('{{LEGEND}}', legend).replace('{{FONTS}}', page_style.LOCAL_FONT_LINK if local else page_style.FONT_LINK).replace('{{BASE}}', page_style.BASE_CSS)
            .replace('{{CHIPS}}', chips)
            .replace('{{HEAD}}', ''.join('<th class="c-%d">%s</th>' % (i, heads.get(c, c)) for i, c in enumerate(show)) + '<th></th>')
            .replace('{{ROWS}}', '\n'.join(trs)))
    open(path, 'w', encoding='utf-8').write(page)


TEMPLATE = '''<!doctype html>
<html lang="zh-Hans"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>玄奘译经清单</title>
{{FONTS}}
<style>{{BASE}}
main{max-width:1240px}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin:18px 0 0}
.chip{display:inline-flex;align-items:baseline;gap:7px;border:1px solid var(--line);background:var(--paper);color:var(--ink);
  border-radius:999px;padding:6px 14px;cursor:pointer;font:500 13.5px/1.2 var(--sans)}
.chip b{font:600 17px/1 var(--zh)}
.chip i{font-style:normal;color:var(--mut);font-size:12px}
.chip.on{border-color:var(--acc);background:var(--acc-soft)}
.dot{width:8px;height:8px;border-radius:50%;display:inline-block;align-self:center;background:var(--mut)}
.s-完整{background:var(--ok)}.s-大部,.s-部分{background:var(--warn)}.s-残片{background:#b98e5a}.s-无{background:var(--line);border:1px solid var(--mut)}
.wrap{border:1px solid var(--line);border-radius:12px;background:var(--paper);overflow:hidden}
table{border-collapse:collapse;width:100%;font-size:14.5px;line-height:1.6}
th,td{padding:10px 12px;text-align:left;vertical-align:baseline}
th{background:var(--soft);font:600 12px/1.4 var(--sans);letter-spacing:.08em;color:var(--mut);white-space:nowrap;border-bottom:1px solid var(--line)}
tr.m{cursor:pointer;border-top:1px solid var(--line)}
tr.m:hover td{background:color-mix(in srgb,var(--acc-soft) 45%,transparent)}
tr.m.open td{background:var(--acc-soft)}
td.c-0,td.c-2,td.c-4{font-family:var(--sans);font-size:13px;color:var(--mut);white-space:nowrap}
td.c-3{font-family:var(--sans);font-size:13px;white-space:nowrap}
td.c-1{font-family:var(--zht);font-weight:600;font-size:16px;letter-spacing:.04em}
td.c-5{font-family:var(--zht);font-size:14px;color:var(--mut)}
td.c-6{font-family:var(--serif);font-style:italic;font-size:15px;word-break:break-word}
td.c-7{font-family:var(--zh);font-size:14px;white-space:nowrap}
td.c-x{color:var(--mut);font-size:12px;text-align:right;width:1%}
tr.d{display:none}tr.d.open{display:table-row}
tr.d td{padding:4px 18px 18px 52px;background:var(--acc-soft)}
dl{margin:0;display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:10px 28px}
dl div{min-width:0}
dt{font:500 11.5px/1.5 var(--sans);letter-spacing:.08em;color:var(--acc)}
dd{margin:2px 0 0;font-family:var(--zh);font-size:14.5px;line-height:1.75}
tr.m[data-s="完整"] td.c-7{color:var(--ok)}tr.m[data-s="大部"] td.c-7,tr.m[data-s="部分"] td.c-7{color:var(--warn)}
tr.hide{display:none!important}
details.legend{margin:16px 0 0;font-family:var(--zh);font-size:14.5px}
details.legend summary{cursor:pointer;font:500 13px/1.4 var(--sans);color:var(--acc);letter-spacing:.04em}
details.legend dl{margin:10px 0 0;padding:14px 16px;background:var(--paper);border:1px solid var(--line);border-radius:10px;grid-template-columns:repeat(auto-fit,minmax(300px,1fr))}
details.legend dt{font-family:var(--serif);font-weight:700;font-size:14px;color:var(--ink);letter-spacing:0}
.tools{display:flex;gap:8px}
.tools button{font:500 13px/1 var(--sans);color:var(--mut);background:var(--paper);border:1px solid var(--line);border-radius:8px;padding:10px 12px;cursor:pointer}
@media (max-width:760px){
  table,tbody,td{display:block}thead{display:none}
  tr.m{display:grid;grid-template-columns:auto auto 1fr auto;grid-template-areas:"t t t x" "s s s s" "a b c c";gap:2px 12px;padding:12px 14px}
  tr.m td{padding:0;background:none!important;white-space:normal}
  td.c-1{grid-area:t}td.c-x{grid-area:x}td.c-6{grid-area:s;font-size:14px}
  td.c-3{grid-area:a}td.c-4{grid-area:b;display:block}td.c-7{grid-area:c}
  td.c-0,td.c-2,td.c-5{display:none}
  tr.m.open{background:var(--acc-soft)}
  tr.d.open{display:block}tr.d td{padding:0 14px 16px}
  dl{grid-template-columns:1fr}
}
</style></head><body><main>
<header class="top">
<p class="kicker">玄奘译语词汇表 · 清单</p>
<h1>玄奘译经清单</h1>
<p class="lead">依据《开元释教录》卷八：玄奘所出七十六部一千三百四十七卷，去掉《大唐西域记》，翻译为 75 部 1335 卷。译出年月与译场取自开元录夹注；梵名、藏译参照 Lancaster《高丽大藏经解题目录》并经核查；梵本状况为人工整理。点击状况筛选，点击一行展开校订本、电子本、同本异译等详情。</p>
<div class="chips">{{CHIPS}}</div>
<details class="legend"><summary>编号与缩略语说明</summary><dl>{{LEGEND}}</dl></details>
</header>
<div class="bar"><input type="search" id="q" placeholder="检索题名、梵名、校订本……" aria-label="检索"><div class="tools"><button id="all">全部展开</button></div></div>
<div class="wrap"><table><thead><tr>{{HEAD}}</tr></thead><tbody>
{{ROWS}}
</tbody></table></div>
</main>
<script>
const M=[...document.querySelectorAll('tr.m')];let f=null,allOpen=false;
M.forEach(r=>r.onclick=e=>{if(e.target.closest('a'))return;const d=r.nextElementSibling;r.classList.toggle('open');d.classList.toggle('open')});
function apply(){const q=document.getElementById('q').value.trim().toLowerCase();
M.forEach(r=>{const d=r.nextElementSibling;const ok=(!f||r.dataset.s===f)&&(!q||(r.textContent+d.textContent).toLowerCase().includes(q));
r.classList.toggle('hide',!ok);d.classList.toggle('hide',!ok)})}
document.querySelectorAll('.chip').forEach(c=>c.onclick=()=>{f=f===c.dataset.f?null:c.dataset.f;
document.querySelectorAll('.chip').forEach(x=>x.classList.toggle('on',x.dataset.f===f));apply()});
document.getElementById('q').oninput=apply;
document.getElementById('all').onclick=e=>{allOpen=!allOpen;M.forEach(r=>{r.classList.toggle('open',allOpen);r.nextElementSibling.classList.toggle('open',allOpen)});e.target.textContent=allOpen?'全部收起':'全部展开'};
</script></body></html>
'''

if __name__ == '__main__':
    main(*sys.argv[1:4])
