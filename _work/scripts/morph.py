"""morph.py -- 形态标注（pos 栏）的格式规则，供 akbh1_morph_apply.py、akbh1_lint.py、akbh1_normalize.py 共用。

名词类（n. adj. pron. num. ptc. gdv. cpd.）：词类 + 性 + 数 + 格，如 "n. m. sg. gen."、"cpd. nt. sg. abl."；
  性不能确定的写 "m./nt."；本身无性的词（第一、二人称代词，五以上的基数词，kati）与 -tas 形式不标性。
  复合词的非末成分：词类 + "成分"，如 "n. 成分"；末成分带整个复合词的词尾，照整个复合词标性数格。
  不变格的复合词："cpd. ind."
动词（v.）：时态/语气 [+ pass.] [+ caus.] + 人称数，如 "v. pres. 3sg."、"v. pres. pass. 3sg."
abs. inf. ind. formula phr. interrog. 及 gram.（语法形式）不要求。
括号内的补充说明（如 "(hata)"、"(bahuvrīhi)"）可放在末尾。
canon(pos) 把性数格、时态语态人称排成上述次序，其余写法不动。
"""
import re

NOMINAL = ('n.', 'adj.', 'pron.', 'num.', 'ptc.', 'gdv.', 'cpd.')
CASE = re.compile(r'\b(nom|acc|instr|dat|abl|gen|loc|voc)\.')
NUM = re.compile(r'(?<![0-9])\b(sg|du|pl)\.')
GENDER = re.compile(r'(?<![\w.])(?:m|f|nt)\.(?:/(?:m|f|nt)\.)*')
TENSE = re.compile(r'\b(pres|impf|perf|aor|fut|opt|impv|cond|prec)\.')
PERSON = re.compile(r'\b[123](sg|du|pl)\.')

# 本身无性的词：第一、二人称代词，五以上的基数词，kati
GENDERLESS = {
    'aham', 'tvam', 'asmad', 'yuṣmad', 'mad', 'tvad', 'kati',
    'pañcan', 'ṣaṣ', 'saptan', 'aṣṭan', 'navan', 'daśan', 'ekādaśan', 'dvādaśan', 'trayodaśan',
    'caturdaśan', 'pañcadaśan', 'ṣoḍaśan', 'saptadaśan', 'aṣṭādaśan',
}

_RANK_NOM = [(GENDER, 0), (NUM, 1), (CASE, 2)]
_RANK_V = [(TENSE, 0), (re.compile(r'\bpass\.'), 1), (re.compile(r'\bcaus\.'), 2), (PERSON, 3)]


def _rank(tok, table):
    for rx, k in table:
        if rx.fullmatch(tok):
            return k
    return None


def _order(part, table):
    """part 中属于 table 的词按次序排好，放回它们原来占的位置；括号内的说明不动。"""
    toks = re.findall(r'\([^)]*\)|\S+', part)
    slots = [i for i, t in enumerate(toks) if not t.startswith('(') and _rank(t, table) is not None]
    vals = sorted((toks[i] for i in slots), key=lambda t: _rank(t, table))
    for i, v in zip(slots, vals):
        toks[i] = v
    return ' '.join(toks)


def canon(pos):
    if not pos:
        return pos
    parts = pos.split(' + ')
    out = []
    for p in parts:
        table = _RANK_V if TENSE.search(re.sub(r'\(.*?\)', '', p)) or PERSON.search(p) else _RANK_NOM
        out.append(_order(p, table))
    return ' + '.join(out)


def _misordered(body, table):
    for p in body.split(' + '):
        ks = [_rank(t, table) for t in p.split()]
        ks = [k for k in ks if k is not None]
        if ks != sorted(ks):
            return True
    return False


def problem(pos, typ='', lemma=''):
    """返回 pos 不合形态标注规则的原因；合规返回空串。"""
    if not pos or pos.startswith('gram') or typ in ('增译', '梵本缺文'):
        return ''
    head = pos.split(' ')[0]
    body = re.sub(r'\(.*?\)', '', pos)
    if head in NOMINAL:
        if '成分' in body or re.search(r'\bcpd\. ind\.', body):
            return ''
        if not CASE.search(body):
            return '名词类缺格'
        if not NUM.search(body):
            return '名词类缺数'
        if not GENDER.search(body) and lemma not in GENDERLESS and '(-tas)' not in pos:
            return '名词类缺性'
        if _misordered(body, _RANK_NOM):
            return '次序应为：词类、性、数、格'
        return ''
    if head == 'v.':
        if not TENSE.search(body):
            return '动词缺时态/语气'
        if not PERSON.search(body):
            return '动词缺人称数'
        if _misordered(body, _RANK_V):
            return '次序应为：时态/语气、pass.、caus.、人称数'
    return ''


# ---- 复合词末成分：带整个复合词的词尾，性数格应与复合词记录一致 ----

def _core(lemma):
    last = lemma.split('-')[-1].split(' ')[0]
    c = re.sub(r'(?:ant|vat|mat|as|us|is|an|in|at|[aāiīuūṛeo])$', '', last)
    c = re.sub(r'[aāiīuū]$', '', c)
    return c if len(c) >= 2 else last


def gnc(pos):
    """pos 中的性、数、格（不计括号内的说明）。"""
    body = re.sub(r'\(.*?\)', '', pos or '')
    return tuple(rx.search(body).group(0) if rx.search(body) else '' for rx in (GENDER, NUM, CASE))


def _is_cased_cpd(r):
    p = r['pos']
    return p.startswith('cpd.') and '成分' not in p and 'cpd. ind.' not in p and CASE.search(re.sub(r'\(.*?\)', '', p))


def final_members(rows):
    """rows：同一单位的记录。返回 [(成分记录, 复合词记录)]：成分的 skt 是复合词 skt 的结尾，
    且成分词目的词干落在 skt 的末尾（其后至多是词尾和连声）。只收名词类，不收增译、语法形式。"""
    bysid = {}
    for r in rows:
        bysid.setdefault(r['sid'], []).append(r)
    out = []
    for rs in bysid.values():
        for c in rs:
            if not c['skt'] or not _is_cased_cpd(c):
                continue
            for m in rs:
                if m is c or not m['skt'] or len(m['skt']) >= len(c['skt']) or not c['skt'].endswith(m['skt']):
                    continue
                if m['type'] in ('增译', '梵本缺文') or m['pos'].split(' ')[0] not in NOMINAL or 'cpd. ind.' in m['pos'] \
                        or m['pos'].startswith('pron.'):   # 代词作末成分极少，多是连声带进的下一个词
                    continue
                core = _core(m['lemma'])
                i = m['skt'].rfind(core)
                if i < 0 or len(m['skt']) - (i + len(core)) > 6:
                    continue
                tail = m['skt'][i + len(core):]
                if 'tv' in tail or re.match(r'[aāiīuū]?(tā|vat|tay)', tail):   # -tva/-tā/-vat 前的词干不是末成分
                    continue
                # 同句另有成分记录落在它的 skt 末尾（如 saṃsparśajā 之后的 jā），它就不是末成分
                if any(o is not m and o is not c and o['skt'] and len(o['skt']) < len(m['skt'])
                       and m['skt'].endswith(o['skt']) and o['pos'].split(' ')[0] in NOMINAL
                       and o['type'] not in ('增译', '梵本缺文') for o in rs):
                    continue
                out.append((m, c))
    return out
