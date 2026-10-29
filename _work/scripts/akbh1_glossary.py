#!/usr/bin/env python3
"""akbh1_glossary.py -- 由对应实例生成词汇表（梵→汉词条、汉→梵索引、语法对应、增译/省译清单）。

Usage: python3 -I akbh1_glossary.py AKBH1_DIR OUT_DIR [NOTES_TSV] [--only=U01,U02,...] [--pkg=PKG_DIR]
  OUT_DIR 写 md 与 csv；--pkg 写离线资料包里的 词汇表.html 与 data/akbh1.js
  --only：只取这些单位（合并、核验完成前，用来只发布已审定的部分）
  读取 AKBH1_DIR/occ/*.tsv（应先用 akbh1_verify.py 核验）、skt_sent.tsv、xz_lines.tsv、pm_lines.tsv
  NOTES_TSV：可选，唐代自注（akbh1_tangnotes.py 的输出），按玄奘译语挂到词条下
输出：OUT_DIR/界品译语实例.csv、界品词汇表.md；PKG_DIR/词汇表.html、data/akbh1.js
"""
import csv
import glob
import html
import json
import os
import re
import sys
import unicodedata
from collections import OrderedDict, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # 同目录的 page_style（-I 模式下不自动加入）
import page_style  # noqa: E402
import abbr  # noqa: E402

ORDER = ['a', 'ā', 'i', 'ī', 'u', 'ū', 'ṛ', 'ṝ', 'ḷ', 'e', 'ai', 'o', 'au', 'ṃ', 'ḥ', 'k', 'kh', 'g', 'gh', 'ṅ',
         'c', 'ch', 'j', 'jh', 'ñ', 'ṭ', 'ṭh', 'ḍ', 'ḍh', 'ṇ', 't', 'th', 'd', 'dh', 'n', 'p', 'ph', 'b', 'bh', 'm',
         'y', 'r', 'l', 'v', 'ś', 'ṣ', 's', 'h']
RANK = {c: i for i, c in enumerate(ORDER)}


def skey(s):
    s = unicodedata.normalize('NFC', s.lower()).lstrip('-√')
    out, i = [], 0
    while i < len(s):
        two = s[i:i + 2]
        if two in RANK and two not in ('ai', 'au') or (two in ('ai', 'au')):
            if two in RANK:
                out.append(RANK[two]); i += 2; continue
        ch = s[i]
        out.append(RANK.get(ch, 100 + ord(ch)) if ch.isalpha() or ch in RANK else 99)
        i += 1
    return out


def tsv(path):
    return list(csv.DictReader(open(path, encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE))


def pref(p):
    """Pradhan '001|03-001|07' → '1.3–7'。GRETIL 页行标记有误的（如空、'03207'）照原样返回。"""
    try:
        parts = [tuple(int(v) for v in x.split('|')) for x in p.split('-')]
        a = '%d.%d' % parts[0]
        if len(parts) > 1 and parts[1] != parts[0]:
            a += '–' + ('%d' % parts[1][1] if parts[1][0] == parts[0][0] else '%d.%d' % parts[1])
        return a
    except (ValueError, IndexError, TypeError):
        return p or '?'


def tref(ln):
    """'0001a08' → 'T29.1a08'"""
    return 'T29.%d%s' % (int(ln[:4]), ln[4:])


def load(d, notes_path, only=None):
    skt = {r['sid']: r for r in tsv(os.path.join(d, 'skt_sent.tsv'))}
    xz = OrderedDict((r['line'], r['text']) for r in tsv(os.path.join(d, 'xz_lines.tsv')))
    pm = OrderedDict((r['line'], r['text']) for r in tsv(os.path.join(d, 'pm_lines.tsv')))
    occ = []
    for f in sorted(glob.glob(os.path.join(d, 'occ', '*.tsv'))):
        if only and os.path.basename(f)[:-4] not in only:
            continue
        occ += tsv(f)
    notes = tsv(notes_path) if notes_path else []
    return skt, xz, pm, occ, notes


SENT_END = '。？！；'


def context(xz, starts, stream, line, frag):
    """取译语所在的整句；只标出起于所引行的那一处。返回（句子，[[起, 止], …]）。"""
    if not frag or line not in starts:
        return '', []
    a0, a1 = starts[line], starts[line] + len(xz[line])
    parts = [p for p in frag.split('…') if p]
    pos = stream.find(parts[0], a0)
    if pos < 0 or pos >= a1:
        return '', []
    spans, cur = [[pos, pos + len(parts[0])]], pos + len(parts[0])
    for p in parts[1:]:
        q = stream.find(p, cur)
        if q < 0 or q - cur > 80:
            break
        spans.append([q, q + len(p)])
        cur = q + len(p)
    b = max(stream.rfind(c, 0, spans[0][0]) for c in SENT_END) + 1
    e = min([x for x in (stream.find(c, spans[-1][1]) for c in SENT_END) if x >= 0] or [len(stream)]) + 1
    b, pre = (b, '') if spans[0][0] - b <= 60 else (spans[0][0] - 40, '…')
    e, post = (e, '') if e - spans[-1][1] <= 60 else (spans[-1][1] + 40, '…')
    ctx = pre + stream[b:e] + post
    off = b - len(pre)
    return ctx, [[x - off, y - off] for x, y in spans]


def main(d, od, notes_path=None, only=None, pkg=None):
    global D_DIR
    D_DIR = d
    skt, xz, pm, occ, notes = load(d, notes_path, only)
    xl = list(xz)
    starts, stream = {}, ''
    for ln, t in xz.items():
        starts[ln] = len(stream)
        stream += t
    for o in occ:
        s = skt[o['sid']]
        o['pradhan'] = pref(s['pradhan'])
        o['karika'] = s['karika']
        o['skt_sent'] = s['text']
        o['T'] = tref(o['xz_line']) if o['xz_line'] else ''
        o['verse'] = s['verse']
        o['xz_ctx'], o['xz_hl'] = context(xz, starts, stream, o['xz_line'], o['xz'])
        o['PM'] = ('T29.%d%s' % (int(o['pm_line'][:4]), o['pm_line'][4:])) if o['pm_line'] else ''
    os.makedirs(od, exist_ok=True)
    cols = ['oid', 'lemma', 'pos', 'skt', 'pradhan', 'karika', 'xz', 'T', 'type', 'pm', 'PM', 'note']
    with open(os.path.join(od, '界品译语实例.csv'), 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction='ignore')
        w.writeheader()
        w.writerows(occ)
    # 词条：按 lemma 汇总。实词、虚词都进词条；省译显示为"（未译）"；
    # 语法对应只收词尾、后缀、句式（pos 以 gram. 起头）；增译单列
    lex = defaultdict(list)
    gram = defaultdict(list)
    add, omit = [], []
    for o in occ:
        if o['type'] in ('增译', '梵本缺文'):
            add.append(o)
            continue
        if o['type'] == '省译':
            omit.append(o)
        if o['pos'].startswith('gram'):
            gram[o['lemma']].append(o)
        elif o['lemma']:
            lex[o['lemma']].append(o)
    def tang_for(rends):
        """唐代自注挂接：注中所给汉译与玄奘译语相同；或注文以该译语起头（如"涅槃，此云圓寂"）。"""
        hit = []
        for n in notes:
            terms = set(n['term'].split('；')) if n['term'] else set()
            for r in rends:
                r = r.replace('…', '')
                if r in terms or re.match(r'[「『]?%s[」』]?[，者]' % re.escape(r), n['text']):
                    hit.append(dict(n, weak=len(r) == 1)); break
        return hit
    entries = []
    for lem in sorted(lex, key=skey):
        os_ = lex[lem]
        rend = OrderedDict()
        for o in os_:
            rend.setdefault(o['xz'] or '（未译）', []).append(o)
        pmr = OrderedDict()
        for o in os_:
            if o['pm']:
                pmr[o['pm']] = pmr.get(o['pm'], 0) + 1
        pos = sorted(set(o['pos'].split(' ')[0] for o in os_))
        tn = tang_for(list(rend))
        entries.append({'lemma': lem, 'pos': '/'.join(pos), 'n': len(os_), 'rend': rend, 'pm': pmr,
                        'cpd': '-' in lem.strip('-'), 'tang': tn})
    rev = defaultdict(lambda: defaultdict(int))
    for o in occ:
        if o['xz'] and o['type'] not in ('增译', '梵本缺文'):
            rev[o['xz']][o['lemma']] += 1
    used, unknown = abbr.scan([o['pos'] for o in occ])
    if unknown:
        print('提示：以下标注未收入缩略语说明表（scripts/abbr.py），请补充：%s' % dict(unknown))
    write_md(entries, gram, add, omit, rev, os.path.join(od, '界品词汇表.md'), len(occ), used)
    if pkg:
        write_html(entries, gram, add, omit, rev, occ, skt, pkg, used)
    print('实例 %d；词条 %d；语法 %d；增译 %d；省译 %d；汉→梵 %d' % (
        len(occ), len(entries), len(gram), len(add), len(omit), len(rev)))


def occ_line(o):
    s = '%s = P %s' % (o['T'].replace('T29.', ''), o['pradhan'])
    return s


def write_md(entries, gram, add, omit, rev, path, n, used):
    L = ['# 俱舍论·界品 玄奘译语词汇表（试点）', '',
         '出处写法：`1a08 = P 1.3` 指大正藏第 29 册 1 页 a 栏 8 行，对应 Pradhan 本第 1 页第 3 行。'
         '"真"后为真谛译（T1559）的对应译语。实例共 %d 条，全部通过出处核验。' % n, '',
         '## 一、梵→汉词条（实词与虚词）', '']
    for e in entries:
        head = '**%s** %s' % (e['lemma'], e['pos'])
        rs = '；'.join('%s（%d）' % (r, len(v)) for r, v in e['rend'].items())
        L.append('- %s — %s' % (head, rs))
        for r, v in e['rend'].items():
            L.append('  - %s：%s' % (r, '；'.join(occ_line(o) for o in v)))
        if e['pm']:
            L.append('  - 真：%s' % '、'.join(e['pm']))
        notes = sorted(set(o['note'] for v in e['rend'].values() for o in v if o['note']))
        for nt in notes:
            L.append('  - 注：%s' % nt)
        for t in e['tang'][:3]:
            L.append('  - 唐代自注（%s %s）：%s%s' % (t['source'], t['ref'], t['text'], '〔仅凭单字译语挂接，待核〕' if t['weak'] else ''))
    L += ['', '## 二、语法形式对应（词尾、后缀、句式）', '']
    for lem in sorted(gram, key=skey):
        v = gram[lem]
        rend = OrderedDict()
        for o in v:
            rend.setdefault(o['xz'], []).append(o)
        L.append('- **%s** — %s' % (lem, '；'.join('%s（%s）' % (r, '；'.join(occ_line(o) for o in x))
                                                for r, x in rend.items())))
        for nt in sorted(set(o['note'] for o in v if o['note'])):
            L.append('  - 注：%s' % nt)
    L += ['', '## 三、增译与梵本缺文', '']
    for o in add:
        L.append('- %s%s（%s）：%s' % ('〔梵本缺文〕' if o['type'] == '梵本缺文' else '', o['xz'], o['T'].replace('T29.', ''), o['note']))
    L += ['', '## 四、省译', '']
    for o in omit:
        L.append('- *%s*（%s，P %s）：%s' % (o['skt'], o['lemma'], o['pradhan'], o['note'] or '未译出'))
    L += ['', '## 五、汉→梵索引', '']
    for zh in sorted(rev):
        L.append('- %s：%s' % (zh, '、'.join('%s（%d）' % (k, c) for k, c in rev[zh].items())))
    L += ['', '## 六、缩略语与体例说明', '', '### 出处写法', '', '| 写法 | 说明 |', '|---|---|']
    L += ['| %s | %s |' % r for r in abbr.REFS]
    L += ['', '### 对应类型', '', '| 类型 | 说明 |', '|---|---|']
    L += ['| %s | %s |' % r for r in abbr.TYPES]
    for g, items in abbr.GROUPS:
        rows = [(a, f, d) for a, f, d in items if used.get(a)]
        if not rows:
            continue
        L += ['', '### ' + g, '', '| 缩写 | 全称 | 说明 | 用例 |', '|---|---|---|---:|']
        L += ['| %s | %s | %s | %d |' % (a, f, d, used[a]) for a, f, d in rows]
    open(path, 'w', encoding='utf-8').write('\n'.join(L) + '\n')


def write_html(entries, gram, add, omit, rev, occ, skt, pkg, used):
    """资料包：PKG/词汇表.html（外壳）＋ PKG/data/akbh1.js（数据：句子、语境去重，实例为紧凑数组）。"""
    tang = {e['lemma']: [{'s': t['source'], 'r': t['ref'], 't': t['text'] + ('〔仅凭单字译语挂接，待核〕' if t['weak'] else '')} for t in e['tang']] for e in entries if e['tang']}
    sents, sidx, ctx, cidx, recs = [], {}, [], {}, []
    for o in occ:
        sid = o['sid']
        if sid not in sidx:
            sidx[sid] = len(sents)
            sents.append([sid, o['pradhan'], o['karika'], o['verse'], o['skt_sent']])
        c = o['xz_ctx']
        if c and c not in cidx:
            cidx[c] = len(ctx)
            ctx.append(c)
        recs.append([o['oid'], o['lemma'], o['pos'], o['skt'], sidx[sid], o['xz'], o['xz_line'], o['type'],
                     o['pm'], o['pm_line'], o['note'], cidx.get(c, -1) if c else -1, o['xz_hl']])
    # 文本信息取自 _work/align/texts.tsv（各文本共用的登记表）
    reg = {r['dir']: r for r in tsv(os.path.join(os.path.dirname(os.path.abspath(D_DIR)), 'texts.tsv'))}
    t = reg[os.path.basename(os.path.abspath(D_DIR))]
    meta = {'part': t['text_id'], 'title': t['short'], 'short': t['short'].split('·')[-1], 'vol': t['vol'], 'work': t['cbeta_work']}
    data = {'meta': meta, 'sents': sents, 'ctx': ctx, 'recs': recs, 'tang': tang}
    os.makedirs(os.path.join(pkg, 'data'), exist_ok=True)
    with open(os.path.join(pkg, 'data', 'akbh1.js'), 'w', encoding='utf-8') as f:
        f.write('XZG_DATA(' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ');\n')
    ab = {'groups': [{'name': g, 'items': [[a, f, d, used[a]] for a, f, d in items if used.get(a)]}
                     for g, items in abbr.GROUPS],
          'refs': abbr.REFS, 'types': abbr.TYPES, 'known': {a: d for a, (f, d) in abbr.KNOWN.items()},
          'alias': abbr.ALIAS}
    js = lambda o: json.dumps(o, ensure_ascii=False).replace('</', '<\\/')  # 防止数据中出现 </script>
    page = (HTML.replace('/*ABBR*/', js(ab)).replace('/*FONTS*/', page_style.LOCAL_FONT_LINK)
            .replace('/*BASE*/', page_style.BASE_CSS).replace('/*DATAFILE*/', 'data/akbh1.js'))
    open(os.path.join(pkg, '词汇表.html'), 'w', encoding='utf-8').write(page)


HTML = r'''<!doctype html>
<html lang="zh-Hans"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>界品译语词汇表</title>
/*FONTS*/
<style>/*BASE*/
.stats{display:flex;flex-wrap:wrap;gap:22px;margin:16px 0 0;font-family:var(--sans);font-size:13px;color:var(--mut)}
.stats b{display:block;font:600 22px/1.2 var(--zh);color:var(--ink);letter-spacing:0}
.e{background:var(--paper);border:1px solid var(--line);border-radius:12px;margin:0 0 12px;transition:border-color .15s;content-visibility:auto;contain-intrinsic-size:auto 96px}
.more{font-family:var(--sans);font-size:13px;color:var(--mut);text-align:center;padding:18px 0}
.e:hover{border-color:color-mix(in srgb,var(--acc) 35%,var(--line))}
.eh{display:grid;grid-template-columns:minmax(150px,240px) 1fr auto;gap:6px 18px;align-items:baseline;padding:14px 18px;cursor:pointer}
.lem{font-family:var(--serif);font-style:italic;font-weight:700;font-size:21px;line-height:1.35;word-break:break-word}
.lem.zh{font-style:normal;font-family:var(--zht);font-size:20px}
.pos{display:block;font-family:var(--sans);font-style:normal;font-weight:400;font-size:12px;color:var(--mut);letter-spacing:.06em;margin-top:2px}
.rs{display:flex;flex-wrap:wrap;gap:6px 8px}
.chip{display:inline-flex;align-items:baseline;gap:5px;background:var(--soft);border-radius:7px;padding:2px 10px;
  font-family:var(--zht);font-size:17px;line-height:1.6}
.chip.sk{font-family:var(--serif);font-style:italic}
.chip i{font:500 11.5px/1 var(--sans);font-style:normal;color:var(--mut)}
.chip.none{color:var(--mut);font-size:14px}
.tog{font-family:var(--sans);font-size:12px;color:var(--mut);white-space:nowrap}
.meta{padding:0 18px 12px;display:grid;gap:4px;font-family:var(--zh);font-size:14.5px;color:var(--mut)}
.meta span.lab{font-family:var(--sans);font-size:11.5px;letter-spacing:.08em;color:var(--acc);margin-right:8px}
.occ{display:none;border-top:1px solid var(--line)}
.e.open .occ{display:block}
.e.open .tog{color:var(--acc)}
.o{display:grid;grid-template-columns:1fr 1fr;gap:6px 22px;padding:12px 18px;border-bottom:1px dashed var(--line)}
.o:last-child{border-bottom:0}
.ref{grid-column:1/-1;font-family:var(--sans);font-size:12px;color:var(--mut);letter-spacing:.03em;display:flex;flex-wrap:wrap;gap:4px 12px;align-items:center}
.ty{border:1px solid var(--line);border-radius:5px;padding:0 6px;font-size:11.5px;color:var(--ink)}
.skt{font-family:var(--serif);font-size:16px;line-height:1.7;color:var(--ink)}
.skt.verse{border-left:3px solid color-mix(in srgb,var(--acc) 45%,transparent);padding-left:10px;font-style:italic}
.xz{font-family:var(--zht);font-size:16.5px;line-height:1.85;letter-spacing:.03em}
mark{background:var(--acc-soft);color:inherit;border-bottom:2px solid var(--acc);padding:0 1px;border-radius:2px}
.note{grid-column:1/-1;font-family:var(--zh);font-size:14px;color:var(--mut)}
.note .lab{font-family:var(--sans);font-size:11.5px;letter-spacing:.06em;margin-right:6px}
.empty{font-family:var(--zh);color:var(--mut);padding:24px 0}
/* 审定 */
.rvbar{grid-column:1/-1;display:flex;flex-wrap:wrap;gap:6px 10px;align-items:center;font-family:var(--sans);font-size:12.5px;color:var(--mut)}
.rvb{font:500 12.5px/1 var(--sans);border:1px solid var(--line);background:var(--paper);color:var(--mut);border-radius:6px;padding:5px 10px;cursor:pointer}
.rvb:hover{border-color:var(--acc);color:var(--acc)}
.rvb.pri{background:var(--acc);border-color:var(--acc);color:#fff}
.badge{border-radius:5px;padding:2px 8px;font-weight:600;font-size:12px}
.b-同意{background:color-mix(in srgb,var(--ok) 16%,transparent);color:var(--ok)}
.b-改正{background:var(--acc-soft);color:var(--acc)}
.b-存疑{background:color-mix(in srgb,var(--warn) 18%,transparent);color:var(--warn)}
.rvform{grid-column:1/-1;border:1px solid var(--line);border-radius:10px;padding:12px 14px;background:var(--bg);display:grid;gap:10px;font-family:var(--sans);font-size:13.5px}
.rvform .vs{display:flex;gap:16px;flex-wrap:wrap}
.rvform .fx{display:grid;grid-template-columns:auto 1fr;gap:6px 10px;align-items:center}
.rvform input[type=text],.rvform select,.rvform textarea{font:15px/1.5 var(--zh);color:var(--ink);background:var(--paper);border:1px solid var(--line);border-radius:6px;padding:5px 8px;min-width:0}
.rvform input.sk{font-family:var(--serif)}
.rvform textarea{min-height:56px;resize:vertical}
.rvform .bt{display:flex;gap:8px;flex-wrap:wrap}
.audit-head{display:flex;flex-wrap:wrap;gap:10px 14px;align-items:center;margin:0 0 16px;padding:14px 16px;background:var(--paper);border:1px solid var(--line);border-radius:12px;font-family:var(--sans);font-size:13.5px}
.audit-head input[type=text]{font:14px/1.4 var(--sans);border:1px solid var(--line);border-radius:6px;padding:6px 9px;background:var(--bg);color:var(--ink);width:9em}
.audit-head .prog{font-weight:600;color:var(--ink)}
.audit-head .grow{flex:1}
.audit-note{font-family:var(--zh);font-size:14px;color:var(--mut);margin:-6px 0 16px}
.warnbox{border:1px solid var(--warn);color:var(--warn);border-radius:8px;padding:8px 12px;font-family:var(--sans);font-size:13px;margin:0 0 12px}
abbr[title]{text-decoration:underline dotted color-mix(in srgb,var(--mut) 60%,transparent);text-underline-offset:3px;cursor:help}
.abs h2{font:700 19px/1.4 var(--zh);margin:28px 0 10px;letter-spacing:.04em}
.abs h2:first-child{margin-top:4px}
table.ab{width:100%;border-collapse:collapse;background:var(--paper);border:1px solid var(--line);border-radius:10px;overflow:hidden;font-size:15px}
table.ab th{background:var(--soft);font:600 12px/1.4 var(--sans);letter-spacing:.08em;color:var(--mut);text-align:left;padding:8px 14px;white-space:nowrap}
table.ab td{padding:8px 14px;border-top:1px solid var(--line);font-family:var(--zh);vertical-align:baseline}
table.ab td.k{font-family:var(--serif);font-weight:700;white-space:nowrap;width:9em}
table.ab td.k.zh{font-family:var(--zh)}
table.ab td.f{font-family:var(--serif);font-style:italic;color:var(--mut);white-space:nowrap}
table.ab td.n{font-family:var(--sans);font-size:13px;color:var(--mut);text-align:right;width:4em}
@media (max-width:720px){table.ab td.f{display:none}table.ab th:nth-child(2){display:none}}
@media (max-width:720px){.eh{grid-template-columns:1fr auto}.rs{grid-column:1/-1}.o{grid-template-columns:1fr}}
</style></head><body><main>
<header class="top">
<p class="kicker">玄奘译语词汇表 · 试点</p>
<h1>俱舍论·界品 译语词汇表</h1>
<p class="lead">范围为界品全品（颂 1.1–1.48，Pradhan 1.3–37.18，T29.1a07–13b09）。每条对应都附梵文原句（Pradhan 本页.行）、玄奘译文（大正藏 T29 页栏行，链接到 CBETA）与真谛译语；点开词条查看全部例句。虚词与语法形式每种对应只收一两例。检索框输入"待核"可筛出待核的条目，详见《待核清单》。</p>
<div class="stats" id="stats"></div>
</header>
<div class="bar">
<input type="search" id="q" placeholder="检索梵文词目、汉译、注或类型，如 abhidharma、對法、待核、梵本缺文" aria-label="检索">
<div class="seg" role="tablist"><button class="on" data-v="lex">梵→汉</button><button data-v="gram">语法形式</button><button data-v="rev">汉→梵</button><button data-v="add">增译 · 省译 · 缺文</button><button data-v="abbr">缩略语</button><button data-v="audit">审定</button></div>
</div>
<div id="out"></div>
</main>
<script type="application/json" id="d-abbr">/*ABBR*/</script>
<script>
const J=id=>JSON.parse(document.getElementById(id).textContent);const AB=J('d-abbr');let D=[],TANG={},META={};
function tl(v,ln){return ln?v+'.'+parseInt(ln.slice(0,4),10)+ln.slice(4):''}
function decode(p){const S=p.sents,C=p.ctx;return p.recs.map(r=>{const s=S[r[4]];return {oid:r[0],lemma:r[1],pos:r[2],skt:r[3],
  pradhan:s[1],karika:s[2],verse:s[3],skt_sent:s[4],xz:r[5],xz_line:r[6],T:tl(p.meta.vol,r[6]),type:r[7],pm:r[8],pm_line:r[9],
  PM:tl(p.meta.vol,r[9]),note:r[10],xz_ctx:r[11]>=0?C[r[11]]:'',xz_hl:r[12]||[]}})}
window.XZG_DATA=function(p){META=p.meta;D=decode(p);TANG=p.tang||{};init()};
const ORDER=['a','ā','i','ī','u','ū','ṛ','ṝ','ḷ','e','ai','o','au','ṃ','ḥ','k','kh','g','gh','ṅ','c','ch','j','jh','ñ','ṭ','ṭh','ḍ','ḍh','ṇ','t','th','d','dh','n','p','ph','b','bh','m','y','r','l','v','ś','ṣ','s','h'];
const R={};ORDER.forEach((c,i)=>R[c]=i);
function key(s){s=s.toLowerCase().normalize('NFC').replace(/^[-√(]+/,'');const o=[];for(let i=0;i<s.length;){const t=s.slice(i,i+2);if(t.length==2&&R[t]!==undefined){o.push(R[t]);i+=2;continue}const c=s[i];o.push(R[c]!==undefined?R[c]:200+c.charCodeAt(0));i++}return o}
const KC=new Map();function ck(s){let k=KC.get(s);if(!k){k=key(s);KC.set(s,k)}return k}
function cmp(a,b){const x=ck(a),y=ck(b);for(let i=0;i<Math.min(x.length,y.length);i++)if(x[i]!=y[i])return x[i]-y[i];return x.length-y.length}
const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
function hlSkt(text,frag){text=text.replace(/\s*\/\/\s*VAkK_[0-9.]+\s*\/\//gi,' //').trim();if(!frag)return esc(text);const i=text.indexOf(frag);
 return i<0?esc(text):esc(text.slice(0,i))+'<mark>'+esc(frag)+'</mark>'+esc(text.slice(i+frag.length))}
function hlZh(text,spans){let h='',k=0;(spans||[]).forEach(([a,b])=>{h+=esc(text.slice(k,a))+'<mark>'+esc(text.slice(a,b))+'</mark>';k=b});return h+esc(text.slice(k))}
function posHTML(p){return esc(p).replace(/loc\. abs\.|[0-9]?[a-zA-Z-]+\.(?:-[a-z]+\.)?|bahuvrīhi|tavat|suffix|abstract|formula|-tas/g,t=>{const k=AB.alias[t]||t;const d=AB.known[k];return d?`<abbr title="${esc(d)}">${t}</abbr>`:t})}
function abbrHTML(){const tb=(head,rows)=>`<table class="ab"><thead><tr>${head.map(h=>`<th>${h}</th>`).join('')}</tr></thead><tbody>${rows.join('')}</tbody></table>`;
 let h=`<section class="abs"><h2>出处写法</h2>${tb(['写法','说明'],AB.refs.map(([a,b])=>`<tr><td class="k">${esc(a)}</td><td>${esc(b)}</td></tr>`))}`;
 h+=`<h2>对应类型</h2>${tb(['类型','说明'],AB.types.map(([a,b])=>`<tr><td class="k zh">${esc(a)}</td><td>${esc(b)}</td></tr>`))}`;
 AB.groups.filter(g=>g.items.length).forEach(g=>{h+=`<h2>${esc(g.name)}</h2>${tb(['缩写','全称','说明','用例'],g.items.map(([a,f,d,n])=>`<tr><td class="k">${esc(a)}</td><td class="f">${esc(f)}</td><td>${esc(d)}</td><td class="n">${n}</td></tr>`))}`});
 const al=Object.entries(AB.alias);if(al.length)h+=`<p class="small">另一写法：${al.map(([a,b])=>`${esc(a)} = ${esc(b)}`).join('；')}</p>`;
 return h+'</section>'}
function cb(o){if(!o.xz_line)return'';return `<a href="https://cbetaonline.dila.edu.tw/zh/${META.work}_p${o.xz_line}" target="_blank" rel="noopener" title="联网时可到 CBETA 查看">${esc(o.T)}</a>`}
function occHTML(o){return `<div class="o"><div class="ref"><span>P ${esc(o.pradhan)}</span>${o.karika?`<span>颂 ${esc(o.karika)}</span>`:''}${cb(o)}<span class="ty">${esc(o.type)}</span>${o.pos?`<span>${posHTML(o.pos)}</span>`:''}</div>
<div class="skt${o.verse=='V'?' verse':''}">${hlSkt(o.skt_sent,o.skt)}</div><div class="xz">${o.xz_ctx?hlZh(o.xz_ctx,o.xz_hl):'<span class="small">（玄奘未译）</span>'}</div>
${o.pm?`<div class="note"><span class="lab">真谛</span>${esc(o.pm)}（${esc(o.PM)}）</div>`:''}${o.note?`<div class="note"><span class="lab">注</span>${esc(o.note)}</div>`:''}${rvBar(o)}</div>`}
function group(list,kf){const m=new Map();list.forEach(o=>{const k=kf(o);if(!m.has(k))m.set(k,[]);m.get(k).push(o)});return m}
const OS=[];
function entry(title,sub,os,rendKey,zhTitle,skChips){const g=group(os,rendKey);const i=OS.push(os)-1;
const rs=[...g].map(([r,v])=>`<span class="chip${skChips?' sk':''}${r=='（未译）'?' none':''}">${esc(r)}<i>${v.length}</i></span>`).join('');
const pm=[...new Set(os.filter(o=>o.pm).map(o=>o.pm))];const tg=(TANG[title]||[]);
const meta=(pm.length?`<div><span class="lab">真谛</span>${pm.map(esc).join('、')}</div>`:'')+tg.map(t=>`<div><span class="lab">唐代自注</span>${esc(t.t)}（${esc(t.s)} ${esc(t.r)}）</div>`).join('');
return `<div class="e"><div class="eh"><div class="lem${zhTitle?' zh':''}">${esc(title)}${sub?`<span class="pos">${posHTML(sub)}</span>`:''}</div><div class="rs">${rs}</div><div class="tog">${os.length} 例 ▾</div></div>
${meta?`<div class="meta">${meta}</div>`:''}<div class="occ" data-i="${i}"></div></div>`}
const ZH={'（未译）':'（未译）'};
let view='lex';const SORTED={};
function sortedGroups(name,list,kf,sorter){if(!SORTED[name]){const g=group(list,kf);SORTED[name]={g,keys:[...g.keys()].sort(sorter)}}return SORTED[name]}
const COLL=new Intl.Collator('zh-Hant-u-co-stroke');
let lexOcc=[],gramOcc=[],BYOID={};
function prep(){lexOcc=D.filter(o=>!['增译','梵本缺文'].includes(o.type)&&!o.pos.startsWith('gram')&&o.lemma);
gramOcc=D.filter(o=>o.pos.startsWith('gram')&&!['增译','梵本缺文'].includes(o.type));BYOID={};D.forEach(o=>BYOID[o.oid]=o)}
const CHUNK=150;let PEND=[],SHOWN=0,IO=null;
function bind(root){root.querySelectorAll('.e .eh').forEach(x=>{if(x.dataset.b)return;x.dataset.b=1;x.onclick=()=>{const e=x.parentNode,o=e.querySelector('.occ');
  if(o&&o.dataset.i!==undefined&&!o.dataset.done){o.innerHTML=OS[+o.dataset.i].map(occHTML).join('');o.dataset.done=1}e.classList.toggle('open')}})}
function more(){const out=document.getElementById('out');const old=out.querySelector('.more');if(old)old.remove();
  const box=document.createElement('div');box.innerHTML=PEND.slice(SHOWN,SHOWN+CHUNK).join('');SHOWN+=CHUNK;
  while(box.firstChild)out.appendChild(box.firstChild);bind(out);
  if(SHOWN<PEND.length){const m=document.createElement('div');m.className='more';m.textContent=`已显示 ${SHOWN} / ${PEND.length}，向下滚动继续`;out.appendChild(m);
    if(IO)IO.disconnect();IO=new IntersectionObserver(es=>{if(es.some(e=>e.isIntersecting))more()},{rootMargin:'800px'});IO.observe(m)}}
function render(){OS.length=0;const q=document.getElementById('q').value.trim().toLowerCase();
const match=o=>!q||[o.lemma,o.skt,o.xz,o.pm,o.note,o.type].join(' ').toLowerCase().includes(q);const H=[];let h='';
if(view=='lex'){const {g,keys}=sortedGroups('lex',lexOcc,o=>o.lemma,cmp);keys.forEach(k=>{const os=g.get(k);if(!os.some(match))return;
  H.push(entry(k,[...new Set(os.map(o=>o.pos.split(' ')[0]))].join(' / '),os,o=>o.xz||'（未译）'))})}
else if(view=='gram'){const {g,keys}=sortedGroups('gram',gramOcc,o=>o.lemma,cmp);keys.forEach(k=>{const os=g.get(k);if(!os.some(match))return;
  H.push(entry(k,AB.known[k]||'语法形式',os,o=>o.xz||'（未译）'))})}
else if(view=='rev'){const {g,keys}=sortedGroups('rev',D.filter(o=>o.xz&&!['增译','梵本缺文'].includes(o.type)),o=>o.xz,COLL.compare);keys.forEach(k=>{const os=g.get(k);if(!os.some(match))return;
  H.push(entry(k,'',os,o=>o.lemma,true,true))})}
else if(view=='abbr'){h=abbrHTML()}
else if(view=='audit'){h=auditHTML()}
else{const os=D.filter(o=>['增译','省译','梵本缺文'].includes(o.type)&&match(o));
  os.forEach(o=>H.push(`<div class="e open"><div class="eh"><div class="lem${o.type!='省译'?' zh':''}">${esc(o.type!='省译'?o.xz:o.skt)}<span class="pos">${o.type=='省译'?'省译 · '+esc(o.lemma):esc(o.type)}</span></div><div></div><div></div></div><div class="occ">${occHTML(o)}</div></div>`))}
const out=document.getElementById('out');if(IO)IO.disconnect();
if(h){out.innerHTML=h;return}
if(!H.length){out.innerHTML='<p class="empty">没有匹配的条目。</p>';return}
out.innerHTML='';PEND=H;SHOWN=0;more()}

/* ===== 审定：结果保存在本浏览器（localStorage），可导出为文件交回 ===== */
let REV={reviewer:'',items:{}},RVOK=true,AF='todo';
const RVTYPES=['对译','意译','音译','拆译','合译','增译','省译','语法','梵本缺文'];
function rkey(){return 'xzg-review-'+(META.part||'x')}
function rvLoad(){try{const s=localStorage.getItem(rkey());if(s)REV=JSON.parse(s);if(!REV.items)REV.items={}}catch(e){RVOK=false}}
function rvSave(){try{localStorage.setItem(rkey(),JSON.stringify(REV))}catch(e){RVOK=false}}
function rvBar(o){const it=REV.items[o.oid];
 return `<div class="rvbar" data-oid="${esc(o.oid)}"><span>${esc(o.oid)}</span>${it?`<span class="badge b-${it.verdict}">${it.verdict}</span>${it.comment?`<span>${esc(it.comment)}</span>`:''}`:''}<button class="rvb" data-act="rv-open">${it?'修改审定':'审定'}</button></div>`}
function rvForm(o){const it=REV.items[o.oid]||{};const v=it.verdict||'同意';const id=o.oid.replace(/[^A-Za-z0-9]/g,'_');
 return `<div class="rvform" data-oid="${esc(o.oid)}">
 <div class="vs">${['同意','改正','存疑'].map(x=>`<label><input type="radio" name="v-${id}" value="${x}"${x==v?' checked':''}> ${x}</label>`).join('')}</div>
 <div class="fx"><span>词目</span><input type="text" class="sk" name="lemma" value="${esc(it.lemma!=null?it.lemma:o.lemma)}">
 <span>译语</span><input type="text" name="xz" value="${esc(it.xz!=null?it.xz:o.xz)}">
 <span>类型</span><select name="type">${RVTYPES.map(t=>`<option${t==(it.type||o.type)?' selected':''}>${t}</option>`).join('')}</select></div>
 <textarea name="comment" placeholder="说明（可选）：理由、正确的读法等">${esc(it.comment||'')}</textarea>
 <div class="small">选"改正"时，词目、译语、类型按上面填写的内容改；选"同意""存疑"时，这三项不改。</div>
 <div class="bt"><button class="rvb pri" data-act="rv-save">保存</button><button class="rvb" data-act="rv-cancel">取消</button>${REV.items[o.oid]?'<button class="rvb" data-act="rv-del">撤销这条审定</button>':''}</div></div>`}
function rvRefresh(oid){document.querySelectorAll(`.rvbar[data-oid="${CSS.escape(oid)}"]`).forEach(b=>b.outerHTML=rvBar(BYOID[oid]));if(view=='audit')render()}
function stamp(){const d=new Date(),z=n=>String(n).padStart(2,'0');return `${d.getFullYear()}${z(d.getMonth()+1)}${z(d.getDate())}-${z(d.getHours())}${z(d.getMinutes())}`}
function rvExport(){const items=Object.entries(REV.items).map(([oid,it])=>Object.assign({oid},it));
 if(!items.length){alert('还没有审定任何条目。');return}
 const out={format:'xzg-review',version:1,part:META.part,title:META.title,reviewer:REV.reviewer||'',exported:new Date().toISOString(),items};
 const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(out,null,1)],{type:'application/json'}));
 a.download=`审定-${META.short||META.part}-${REV.reviewer||'未署名'}-${stamp()}.json`;document.body.appendChild(a);a.click();setTimeout(()=>{URL.revokeObjectURL(a.href);a.remove()},1000)}
function rvImport(file){const fr=new FileReader();fr.onload=()=>{try{const x=JSON.parse(fr.result);if(x.format!=='xzg-review')throw 0;
  if(x.part&&x.part!==META.part&&!confirm(`这个文件是"${x.title||x.part}"的审定结果，与当前页面不同，仍要导入吗？`))return;
  let n=0,k=0;(x.items||[]).forEach(it=>{const cur=REV.items[it.oid];if(!BYOID[it.oid]){k++;return}
   if(!cur||(it.ts||0)>(cur.ts||0)){const c=Object.assign({},it);delete c.oid;REV.items[it.oid]=c;n++}});
  if(!REV.reviewer&&x.reviewer)REV.reviewer=x.reviewer;rvSave();render();alert(`导入 ${n} 条${k?`；${k} 条在当前数据中找不到，已跳过`:''}。`)}catch(e){alert('无法读取：这不是审定结果文件。')}};fr.readAsText(file,'utf-8')}
function auditHTML(){const Q=D.filter(o=>o.note.includes('待核')||o.type=='梵本缺文'||o.pos.includes('(?)')||REV.items[o.oid]);
 const done=Q.filter(o=>REV.items[o.oid]).length,all=Object.keys(REV.items).length;
 const L=Q.filter(o=>AF=='all'||(AF=='todo')==!REV.items[o.oid]);
 const head=`${RVOK?'':'<div class="warnbox">这个浏览器不允许本地保存（可能是隐私模式），关闭页面后审定结果会丢失，请及时导出。</div>'}
 <div class="audit-head"><span class="prog">待审 ${Q.length-done} · 已审 ${done}</span><span class="small">（全部已审定 ${all} 条，含其他例句）</span>
 <span class="seg">${[['todo','未审'],['done','已审'],['all','全部']].map(([k,t])=>`<button data-act="af" data-af="${k}" class="${AF==k?'on':''}">${t}</button>`).join('')}</span>
 <span class="grow"></span><label>审定人 <input type="text" id="rv-name" value="${esc(REV.reviewer||'')}" placeholder="署名"></label>
 <button class="rvb pri" data-act="rv-export">导出审定结果</button><button class="rvb" data-act="rv-import">导入</button><input type="file" id="rv-file" accept=".json,application/json" hidden></div>
 <p class="audit-note">这里集中列出标"待核"的对应、梵本缺文和形态存疑（词性栏带 (?)）的条目；形态的意见请写在"说明"里。其他任何例句下面也都有"审定"按钮，审过的会一并列入。审定结果自动保存在本浏览器里；导出的文件交给编者即可。</p>`;
 return head+(L.length?L.map(o=>`<div class="e open"><div class="eh"><div class="lem${o.lemma?'':' zh'}">${esc(o.lemma||o.xz)}<span class="pos">${esc(o.type)}${o.pos?' · '+posHTML(o.pos):''}</span></div><div></div><div></div></div><div class="occ">${occHTML(o)}</div></div>`).join(''):'<p class="empty">这一栏没有条目。</p>')}
document.addEventListener('click',e=>{const b=e.target.closest('[data-act]');if(!b)return;const act=b.dataset.act;
 if(act=='af'){AF=b.dataset.af;render();return}
 if(act=='rv-export'){rvExport();return}
 if(act=='rv-import'){document.getElementById('rv-file').click();return}
 const box=b.closest('[data-oid]');if(!box)return;const oid=box.dataset.oid,o=BYOID[oid];
 if(act=='rv-open'){const nx=box.nextElementSibling;if(nx&&nx.classList.contains('rvform'))return;box.insertAdjacentHTML('afterend',rvForm(o));return}
 if(act=='rv-cancel'){box.remove();return}
 if(act=='rv-del'){if(confirm('撤销这条审定？')){delete REV.items[oid];rvSave();box.remove();rvRefresh(oid)}return}
 if(act=='rv-save'){const f=box,v=f.querySelector('input[type=radio]:checked').value,
   it={verdict:v,comment:f.querySelector('[name=comment]').value.trim(),ts:Date.now(),reviewer:REV.reviewer||'',
       orig:{lemma:o.lemma,xz:o.xz,type:o.type}};
   if(v=='改正'){it.lemma=f.querySelector('[name=lemma]').value.trim();it.xz=f.querySelector('[name=xz]').value.trim();it.type=f.querySelector('[name=type]').value;
     if(it.lemma==o.lemma&&it.xz==o.xz&&it.type==o.type&&!it.comment){alert('选了"改正"，但词目、译语、类型都没有改，也没有写说明。');return}}
   REV.items[oid]=it;rvSave();box.remove();rvRefresh(oid)}});
document.addEventListener('input',e=>{if(e.target.id=='rv-name'){REV.reviewer=e.target.value.trim();rvSave()}});
document.addEventListener('change',e=>{if(e.target.id=='rv-file'&&e.target.files[0]){rvImport(e.target.files[0]);e.target.value=''}});

function init(){prep();rvLoad();
document.getElementById('stats').innerHTML=[['对应实例',D.length],['梵文词目',new Set(lexOcc.map(o=>o.lemma)).size],['语法形式',new Set(gramOcc.map(o=>o.lemma)).size],['增译',D.filter(o=>o.type=='增译').length],['省译',D.filter(o=>o.type=='省译').length],['梵本缺文',D.filter(o=>o.type=='梵本缺文').length]].map(([a,b])=>`<div><b>${b}</b>${a}</div>`).join('');
render()}
document.querySelectorAll('.seg button').forEach(t=>t.onclick=()=>{view=t.dataset.v;document.querySelectorAll('.seg button').forEach(x=>x.classList.toggle('on',x===t));render()});
document.getElementById('q').oninput=render;
</script>
<script src="/*DATAFILE*/" charset="utf-8"></script>
</body></html>
'''

if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    only = [a[7:].split(',') for a in sys.argv[1:] if a.startswith('--only=')]
    pkg = [a[6:] for a in sys.argv[1:] if a.startswith('--pkg=')]
    main(*args[:3], only=set(only[0]) if only else None, pkg=pkg[0] if pkg else None)
