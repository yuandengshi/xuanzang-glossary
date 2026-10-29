"""abbr.py -- 词汇表中词类、语法标注所用缩略语的说明（页面"缩略语"表与悬停提示的来源）。

GROUPS：分组的 (缩写, 全称, 说明)。ALIAS：同义的另一写法 → 标准写法。
scan(pos_list) 统计实际用到的缩写，并返回未收入说明表的写法，供生成时提示补充。
"""
import re
from collections import Counter

GROUPS = [
    ('词类', [
        ('n.', 'noun', '名词'),
        ('adj.', 'adjective', '形容词'),
        ('pron.', 'pronoun', '代词（含关系代词、疑问代词）'),
        ('num.', 'numeral', '数词'),
        ('ord.', 'ordinal', '序数词，如 prathama（第一）'),
        ('ind.', 'indeclinable', '不变词：副词、小品词、连词、否定词等'),
        ('adv.', 'adverb', '副词'),
        ('interrog.', 'interrogative', '疑问词'),
        ('phr.', 'phrase', '短语、固定说法'),
        ('v.', 'verb', '动词的限定形式'),
        ('ptc.', 'participle', '分词；词目写分词本身（如 hata、ukta、paśyat），所从出的词根注在 pos 末尾的括号里，如 (√han)'),
        ('√', 'root', '词根，如 (√han)、(caus. √jan)'),
        ('ppp.', 'past passive participle', '过去被动分词（-ta、-na），玄奘常以"已"表出'),
        ('tavat', 'past active participle', '过去主动分词（-tavat），如 abhyuddhṛtavān'),
        ('gdv.', 'gerundive', '动形容词（-ya、-tavya、-anīya），表"应…、可…"，玄奘常译"所…"；词目写词形本身（如 vaktavya），词根注在括号里'),
        ('abs.', 'absolutive', '独立式（-tvā、-ya），表先行动作，玄奘常以"已"表出'),
        ('inf.', 'infinitive', '不定式（-tum）'),
        ('cpd.', 'compound', '复合词，词目用连字符分出成分'),
        ('成分', '', '复合词的非末成分（本身不变格）；末成分带整个复合词的词尾，照整个复合词标性数格；"cpd. ind." 为不变格的复合词'),
        ('bahuvrīhi', 'bahuvrīhi', '多财释（"具有…者"的复合词，"具有…者"）'),
        ('formula', 'formula', '套语，如 oṃ namo buddhāya'),
        ('人名', '', '人名'),
    ]),
    ('性', [
        ('m.', 'masculine', '阳性'),
        ('f.', 'feminine', '阴性'),
        ('nt.', 'neuter', '中性；"m./nt." 表示据词形和上下文不能确定'),
    ]),
    ('格', [
        ('nom.', 'nominative', '第一格'),
        ('acc.', 'accusative', '第二格'),
        ('instr.', 'instrumental', '第三格，玄奘常以"由""以""因"表出'),
        ('dat.', 'dative', '第四格'),
        ('abl.', 'ablative', '第五格，表原因时玄奘常译"故""由"'),
        ('gen.', 'genitive', '第六格'),
        ('loc.', 'locative', '第七格'),
        ('loc. abs.', 'locative absolute', '第七格独立结构，玄奘常译"若…者"'),
        ('gen. abs.', 'genitive absolute', '第六格独立结构（现在分词第六格），玄奘或译"若"'),
        ('abl. compar.', 'ablative of comparison', '表比较的第五格（"异于…"），玄奘以"異"表出'),
        ('voc.', 'vocative', '呼格'),
    ]),
    ('数与人称', [
        ('sg.', 'singular', '单数'),
        ('du.', 'dual', '双数'),
        ('pl.', 'plural', '复数，玄奘常以"諸"表出'),
        ('1sg.', 'first person singular', '第一人称单数'),
        ('1pl.', 'first person plural', '第一人称复数'),
        ('2sg.', 'second person singular', '第二人称单数'),
        ('3sg.', 'third person singular', '第三人称单数'),
        ('3pl.', 'third person plural', '第三人称复数'),
        ('3du.', 'third person dual', '第三人称双数'),
    ]),
    ('时态、语气、语态', [
        ('pres.', 'present', '现在时'),
        ('impf.', 'imperfect', '未完成过去时'),
        ('perf.', 'perfect', '完成时'),
        ('aor.', 'aorist', '不定过去时'),
        ('fut.', 'future', '将来时，玄奘常以"當""欲"表出'),
        ('opt.', 'optative', '祈愿语气，玄奘常以"應""則為"表出'),
        ('impv.', 'imperative', '命令语气'),
        ('cond.', 'conditional', '条件语气'),
        ('act.', 'active', '主动语态；与被动对举时玄奘常以"能"对"所"'),
        ('pass.', 'passive', '被动'),
        ('caus.', 'causative', '使役，玄奘常以"令"表出'),
        ('desid.', 'desiderative', '愿望式（-sa-），表"欲…"'),
        ('pres. ptc.', 'present participle', '现在分词，玄奘或以"正…時""時"表出'),
    ]),
    ('比较与构词', [
        ('compar.', 'comparative', '比较级（-tara、-īyas）'),
        ('superl.', 'superlative', '最高级（-tama、-iṣṭha）'),
        ('suffix', 'suffix', '后缀，如 -vat（如、猶如）'),
        ('abstract', 'abstract suffix', '抽象名词后缀（-tva、-tā），玄奘常以"是""性"表出'),
        ('-tas', 'adverbial suffix -tas', '副词后缀，表"从…、就…而言"'),
        ('neg.', 'negative prefix', '否定前缀 a-/an-'),
        ('agent', 'agent suffix', '施事后缀（-aka 等），表"能…者"'),
        ('dvandva', 'dvandva', '相违释（并列复合词），玄奘或以"與""及"连接'),
        ('āmreḍita', 'āmreḍita', '叠词（如 pṛthak pṛthak），玄奘多作"各各""各別"'),
        ('gram.', 'grammatical form', '语法形式：格尾、后缀、句式等，词目以"-"或句式写出，如 -āt (abl.)、santi … yeṣām'),
        ('rel.-cor.', 'relative-correlative', '关系-相关句（yad … tad），玄奘常译"…名為…""謂…"'),
    ]),
]

ALIAS = {'comp.': 'compar.', 'gerundive': 'gdv.'}

# 页面上的出处写法、对应类型（固定说明，不依赖扫描）
REFS = [
    ('P 1.3–7', 'Pradhan 本（1975 年修订第 2 版）第 1 页第 3–7 行；跨页写作 P 1.22–2.1'),
    ('T29.1a09', '大正藏第 29 册第 1 页 a 栏第 9 行（玄奘译 T1558），点击可到 CBETA'),
    ('T29.161c08', '真谛译（T1559）的出处，写法同上'),
    ('颂 1.1', '第一品（界品）第 1 颂；1.2ab、1.2cd 指一颂的前后半；颂 2.1 为第二品（根品）第 1 颂'),
    ('U01-003', '对应实例编号：单位 U01 的第 3 条'),
    ('…', '不连续的译语，如"拔…出"'),
    ('（未译）', '该词此处玄奘没有译出（省译）'),
]

TYPES = [
    ('对译', '固定的、逐词的对当，如 abhidharma → 對法'),
    ('意译', '按意思改写，不逐词对当'),
    ('音译', '如 abhidharma → 阿毘達磨'),
    ('拆译', '一个梵文词拆成两个以上的汉语成分，如 pratibandha → 覆…障'),
    ('合译', '两个以上的梵文词合成一个汉语译语'),
    ('增译', '玄奘译文有、梵文没有的成分'),
    ('省译', '梵文有、玄奘没有译出的成分'),
    ('梵本缺文', '两个汉译（玄奘、真谛）都有、现存梵本（GRETIL/Pradhan）没有的内容，疑二人所据梵本有之，不算玄奘增译'),
    ('语法', '用汉语虚词或句式对应梵文的语法形式或虚词'),
]

KNOWN = {a: (full, desc) for _, items in GROUPS for a, full, desc in items}


def tokens(pos):
    """把 pos 拆成缩写；括号里写的是词形或说明（如 ptc. (hata)），只取其中的缩写。"""
    out = []
    p = pos.replace('loc. abs.', 'loc.abs.')
    for t in re.split(r'[\s/+()]+', p):
        t = t.strip()
        if not t:
            continue
        t = 'loc. abs.' if t == 'loc.abs.' else ALIAS.get(t, t)
        out.append('√' if t.startswith('√') else t)
    return out


def scan(pos_list):
    used, unknown = Counter(), Counter()
    for p in pos_list:
        for t in tokens(p):
            if t in KNOWN:
                used[t] += 1
            elif t.endswith('.') or t in ('-tas',):
                unknown[t] += 1
    return used, unknown
