#!/usr/bin/env python3
"""akbh1_normalize.py -- 合并七批子代理的实例后统一写法（2026-10-29 合并时制定的规则）。

Usage: python3 -I akbh1_normalize.py AKBH1_DIR [--dry]
规则：
 1. 语法形式按范畴立目（玄奘的处理取决于范畴，不取决于具体词尾）。原词尾移入 pos，如
    "-aiḥ (instr. pl.)" → lemma "instr."，pos "gram. instr. pl. (-aiḥ)"。
    复数词尾对作"諸""眾"的归"pl."；对作其他汉字的归各自的格。
 2. comp. → compar.
 3. 实词词目：否定前缀加连字符（a-bhāva、a-jñāna），复合词成分一律用词干（cakṣus-、manas-、catur-、adhas-），
    合写的 manovijñāna、cakṣurvijñāna 拆为 manas-vijñāna、cakṣus-vijñāna；分词、形容词不拆前缀（saṃprayukta）。
    单用的基数词用 -an 词干（pañca → pañcan）；复合词里仍作 pañca-、daśa-、ṣaṣ-。
 4. 形态标注排成规定次序（morph.canon）：词类、性、数、格；动词为时态/语气、pass.、caus.、人称数。
"""
import csv
import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import morph  # noqa: E402

CASE = {'abl': 'abl.', 'instr': 'instr.', 'gen': 'gen.', 'loc': 'loc.', 'dat': 'dat.', 'acc': 'acc.', 'nom': 'nom.'}
FIXED = {  # 原 lemma（括号内标签）→ 范畴
    'fut.': 'fut.', 'ppp.': 'ppp.', 'abs.': 'abs.', 'gdv.': 'gdv.', 'pass.': 'pass.', 'caus.': 'caus.',
    'desid.': 'desid.', 'opt.': 'opt.', 'impv.': 'impv.', 'impf.': 'impf.', 'pres.': 'pres.',
    'pres. ptc.': 'pres. ptc.', 'ptc. pres.': 'pres. ptc.', 'ptc. pres. gen.': 'gen. abs.',
    'act.': 'act.', 'act. 3sg.': 'act.', '1sg.': '1sg.', '1pl.': '1pl.', '3pl.': '3pl.',
    'comp.': 'compar.', 'compar.': 'compar.', 'loc. abs.': 'loc. abs.', 'du.': 'du.',
    'abl. of comparison': 'abl. compar.', 'abl. (comparison)': 'abl. compar.',
}
KEEP = re.compile(r'^(-tva \(abstract\)|-vat|-artham|-arthena|-aka \(agent\)|a- \(neg\.\)|dvandva|\(āmreḍita\)|'
                  r'santi … yeṣām|yad … tad|yadā … tadā|kim … āhosvit)$')
LEX = {'abhāva': 'a-bhāva', 'ananta': 'an-anta', 'anityatā': 'a-nityatā', 'avijñapti-varjya': 'a-vijñapti-varjya',
       'bhavāgra': 'bhava-agra', 'ekadeśa': 'eka-deśa', 'pra-jñā': 'prajñā', 'sahabhū': 'saha-bhū', 'sahaja': 'saha-ja',
       # 2026-10-29 建规范词目表前补充
       'ajñāna': 'a-jñāna', 'anantara': 'an-antara', 'apratisaṃkhyā': 'a-pratisaṃkhyā',
       'saṃ-pra-yukta': 'saṃprayukta'}
# 复合词成分：连声形式 → 词干
MEMBER = {'cakṣur': 'cakṣus', 'mano': 'manas', 'manaḥ': 'manas', 'catuḥ': 'catur', 'catuṣ': 'catur', 'adho': 'adhas'}


def gram_lemma(lemma, pos, xz):
    """返回（新 lemma, 新 pos）；不是要并条的语法形式就返回 None。"""
    if KEEP.match(lemma):
        if lemma == '-arthena':
            return '-artham', pos + ' (-arthena)'
        if lemma == '(āmreḍita)':
            return 'āmreḍita', pos
        return None
    if lemma == 'sat (loc. abs.)':
        return 'loc. abs.', 'gram. loc. abs. (sati)'
    m = re.match(r'^(-?[^\s(]+-?)\s*\((.+)\)$', lemma)
    if not m:
        return None
    ending, lab = m.group(1), m.group(2).strip()
    if ending.startswith('-') or ending == 'sat':
        pass
    else:
        return None
    if 'pl.' in lab and re.search('[諸眾]', xz or ''):
        cat = 'pl.'
    elif lab in FIXED:
        cat = FIXED[lab]
    else:
        c = re.match(r'(abl|instr|gen|loc|dat|acc|nom)\.', lab)
        if c:
            cat = CASE[c.group(1)]
        elif lab in ('pl.',):
            cat = 'pl.'
        else:
            return None
    return cat, 'gram. %s (%s)' % (lab, ending)


def lex_lemma(l, pos):
    if l in LEX:
        l = LEX[l]
    if l.startswith('anutpatti-'):
        l = 'an-utpatti-' + l[len('anutpatti-'):]
    if l == 'ā-khyā' and pos.startswith('n'):
        l = 'ākhyā'
    if l == 'pañca':
        return 'pañcan'
    if l.startswith(('ṣaṭ-', 'ṣaḍ-')):
        l = 'ṣaṣ-' + l[len('ṣaṭ-'):]
    parts = l.split('-')
    # 否定前缀：apratisaṃkhyā-nirodha、anutpatti-dharman 等复合词的首成分
    if parts[0] in LEX:
        parts = LEX[parts[0]].split('-') + parts[1:]
    out = []
    for p in parts:
        if p in MEMBER:
            p = MEMBER[p]
        elif p == 'manovijñāna':
            p = 'manas-vijñāna'
        elif p == 'cakṣurvijñāna':
            p = 'cakṣus-vijñāna'
        out.append(p)
    return '-'.join(out)


def main(d, dry):
    stats = {'gram': 0, 'comp': 0, 'lex': 0, 'order': 0}
    for f in sorted(glob.glob(os.path.join(d, 'occ', 'U*.tsv')) + glob.glob(os.path.join(d, 'occ_extra', 'U*.tsv'))):
        hdr = open(f, encoding='utf-8').readline().rstrip('\n').split('\t')
        rows = list(csv.DictReader(open(f, encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE))
        for r in rows:
            if r['pos'].startswith('gram') or r['lemma'].startswith('-') or r['lemma'].startswith('sat ('):
                g = gram_lemma(r['lemma'], r['pos'], r['xz'])
                if g and (g[0] != r['lemma']):
                    r['lemma'], r['pos'] = g; stats['gram'] += 1
            elif r['lemma']:
                nl = lex_lemma(r['lemma'], r['pos'])
                if nl != r['lemma']:
                    r['lemma'] = nl; stats['lex'] += 1
            # 放在并条之后：并条会用原标签重写 pos
            if re.search(r'\bcomp\.', r['pos']):
                r['pos'] = re.sub(r'\bcomp\.', 'compar.', r['pos']); stats['comp'] += 1
            c = morph.canon(r['pos'])
            if c != r['pos']:
                r['pos'] = c; stats['order'] += 1
        if not dry:
            with open(f, 'w', encoding='utf-8') as fo:
                fo.write('\t'.join(hdr) + '\n')
                for r in rows:
                    fo.write('\t'.join(r[h] for h in hdr) + '\n')
    print(('（试算）' if dry else '') + '语法形式并条 %(gram)d，comp.→compar. %(comp)d，实词词目统一 %(lex)d，形态次序 %(order)d' % stats)


if __name__ == '__main__':
    main(sys.argv[1], '--dry' in sys.argv[2:])
