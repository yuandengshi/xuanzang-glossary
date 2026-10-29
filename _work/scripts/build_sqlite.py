#!/usr/bin/env python3
"""build_sqlite.py -- 由 TSV 工作数据生成 SQLite 查询库（派生文件，不在上面编辑）。

Usage: python3 -I build_sqlite.py ALIGN_DIR INVENTORY_CSV OUT.sqlite
  ALIGN_DIR：_work/align（读 texts.tsv、lemmas.tsv 及各文本目录下的 occ/、occ_extra/、skt_sent.tsv、xz_lines.tsv、pm_lines.tsv、tangnotes.tsv、units_map.tsv）
表：texts、units、skt_sentences、zh_lines、records（含存档的虚词例句，archived=1）、lemmas、tang_notes、inventory、_说明
视图：v_records（实例连原文）、v_renderings（词目各译法及次数）
"""
import csv
import glob
import os
import sqlite3
import sys


def tsv(p):
    return list(csv.DictReader(open(p, encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE))


SCHEMA = '''
CREATE TABLE texts(text_id TEXT PRIMARY KEY, title TEXT, short TEXT, taisho TEXT, cbeta_work TEXT, vol TEXT, juan TEXT,
  xz_translator TEXT, pm_text TEXT, pm_translator TEXT, skt_source TEXT);
CREATE TABLE units(text_id TEXT, unit TEXT, karika TEXT, xz_line TEXT, skt_sid TEXT, pm_line TEXT, PRIMARY KEY(text_id, unit));
CREATE TABLE skt_sentences(text_id TEXT, sid TEXT, unit TEXT, pradhan TEXT, verse INTEGER, karika TEXT, text TEXT, PRIMARY KEY(text_id, sid));
CREATE TABLE zh_lines(text_id TEXT, version TEXT, line TEXT, text TEXT, PRIMARY KEY(text_id, version, line));
CREATE TABLE records(text_id TEXT, oid TEXT, unit TEXT, sid TEXT, skt TEXT, lemma TEXT, pos TEXT, xz_line TEXT, xz TEXT,
  type TEXT, pm_line TEXT, pm TEXT, note TEXT, archived INTEGER DEFAULT 0, PRIMARY KEY(text_id, oid));
CREATE INDEX ix_rec_lemma ON records(lemma);
CREATE INDEX ix_rec_xz ON records(xz);
CREATE INDEX ix_rec_type ON records(type);
CREATE INDEX ix_rec_sid ON records(text_id, sid);
CREATE TABLE lemmas(lemma TEXT PRIMARY KEY, class TEXT, count INTEGER, renderings TEXT, variants TEXT, status TEXT, note TEXT);
CREATE TABLE tang_notes(text_id TEXT, source TEXT, ref TEXT, term TEXT, skt_tr TEXT, text TEXT);
CREATE VIEW v_records AS
  SELECT r.text_id, r.oid, r.unit, r.lemma, r.pos, r.skt, r.xz, r.type, r.pm, r.note, r.archived,
         s.pradhan, s.karika, s.verse, s.text AS skt_sentence,
         r.xz_line, z.text AS xz_line_text, r.pm_line, p.text AS pm_line_text
  FROM records r
  LEFT JOIN skt_sentences s ON s.text_id = r.text_id AND s.sid = r.sid
  LEFT JOIN zh_lines z ON z.text_id = r.text_id AND z.version = '玄奘' AND z.line = r.xz_line
  LEFT JOIN zh_lines p ON p.text_id = r.text_id AND p.version = '真谛' AND p.line = r.pm_line;
CREATE VIEW v_renderings AS
  SELECT lemma, xz, type, COUNT(*) AS n, SUM(archived) AS archived_n, MIN(text_id || ':' || oid) AS first_oid
  FROM records WHERE type NOT IN ('增译', '梵本缺文') AND lemma != '' GROUP BY lemma, xz, type;
CREATE TABLE _说明(对象 TEXT, 字段 TEXT, 说明 TEXT);
'''

DOC = [
    ('texts', '', '收录的文本；text_id 是各表共用的文本编号'),
    ('units', '', '对齐单位（以颂为锚）：玄奘起始行、梵本起始句、真谛起始行'),
    ('skt_sentences', '', '梵本句子（GRETIL）；pradhan 为 Pradhan 本页|行，verse=1 为本颂'),
    ('zh_lines', '', '汉译逐行原文；version 为"玄奘"或"真谛"，line 为大正藏页栏行（如 0001a08）'),
    ('records', '', '对应实例：一个梵文词语与玄奘译语在某一处的对应'),
    ('records', 'skt', '梵文原形（GRETIL 拼写，连声照录）'),
    ('records', 'lemma', '词目；语法形式以范畴立目，如 abl.（第五格）、pl.（复数）'),
    ('records', 'xz / xz_line', '玄奘译语及其大正藏行号；"…"表示不连续'),
    ('records', 'type', '对译、意译、音译、拆译、合译、增译、省译、语法、梵本缺文'),
    ('records', 'pm / pm_line', '真谛译语及其行号'),
    ('records', 'archived', '1 = 按"虚词每种对应一两例"未收入词汇表、存档的例句；统计频次时可一并计入'),
    ('lemmas', '', '规范词目表：标准写法、词类、出现次数、主要译法、异写'),
    ('tang_notes', '', '唐代注疏中的梵汉对照自注（普光记、法宝疏、玄应音义）'),
    ('inventory', '', '玄奘译经清单（开元录所载 76 部）'),
    ('v_records', '', '视图：实例连同梵文句、玄奘与真谛所在行的原文'),
    ('v_renderings', '', '视图：每个词目的各种译法及次数（含存档例句）'),
]


def main(align, inv_csv, out):
    if os.path.exists(out):
        os.remove(out)
    db = sqlite3.connect(out)
    db.executescript(SCHEMA)
    texts = tsv(os.path.join(align, 'texts.tsv'))
    for t in texts:
        db.execute('INSERT INTO texts VALUES (?,?,?,?,?,?,?,?,?,?,?)', [t[k] for k in (
            'text_id', 'title', 'short', 'taisho', 'cbeta_work', 'vol', 'juan', 'xz_translator', 'pm_text', 'pm_translator', 'skt_source')])
        d = os.path.join(align, t['dir'])
        tid = t['text_id']
        um = tsv(os.path.join(d, 'units_map.tsv'))
        db.executemany('INSERT INTO units VALUES (?,?,?,?,?,?)', [(tid, u['unit'], u['karika'], u['xz_line'], u['skt_sid'], u['pm_line']) for u in um])
        starts = [(u['skt_sid'], u['unit']) for u in um]
        def unit_of(sid):
            cur = starts[0][1]
            for s0, u in starts:
                if sid >= s0:
                    cur = u
            return cur
        db.executemany('INSERT INTO skt_sentences VALUES (?,?,?,?,?,?,?)', [
            (tid, s['sid'], unit_of(s['sid']), s['pradhan'], 1 if s['verse'] == 'V' else 0, s['karika'], s['text'])
            for s in tsv(os.path.join(d, 'skt_sent.tsv'))])
        for ver, fn in (('玄奘', 'xz_lines.tsv'), ('真谛', 'pm_lines.tsv')):
            db.executemany('INSERT INTO zh_lines VALUES (?,?,?,?)', [(tid, ver, r['line'], r['text']) for r in tsv(os.path.join(d, fn))])
        for sub, arch in (('occ', 0), ('occ_extra', 1)):
            for f in sorted(glob.glob(os.path.join(d, sub, 'U*.tsv'))):
                u = os.path.basename(f)[:-4]
                db.executemany('INSERT INTO records VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)', [
                    (tid, r['oid'], u, r['sid'], r['skt'], r['lemma'], r['pos'], r['xz_line'], r['xz'], r['type'],
                     r['pm_line'], r['pm'], r['note'], arch) for r in tsv(f)])
        tn = os.path.join(d, 'tangnotes.tsv')
        if os.path.exists(tn):
            db.executemany('INSERT INTO tang_notes VALUES (?,?,?,?,?,?)', [(tid, r['source'], r['ref'], r['term'], r['skt_tr'], r['text']) for r in tsv(tn)])
    db.executemany('INSERT INTO lemmas VALUES (?,?,?,?,?,?,?)', [
        (r['lemma'], r['class'], int(r['count'] or 0), r['renderings'], r['variants'], r['status'], r['note'])
        for r in tsv(os.path.join(align, 'lemmas.tsv'))])
    inv = list(csv.DictReader(open(inv_csv, encoding='utf-8-sig')))
    cols = list(inv[0].keys())
    db.execute('CREATE TABLE inventory(%s)' % ', '.join('"%s" TEXT' % c for c in cols))
    db.executemany('INSERT INTO inventory VALUES (%s)' % ','.join('?' * len(cols)), [[r[c] for c in cols] for r in inv])
    db.executemany('INSERT INTO _说明 VALUES (?,?,?)', DOC)
    db.commit()
    n = db.execute('SELECT COUNT(*), SUM(archived) FROM records').fetchone()
    print('SQLite：实例 %d 条（其中存档 %d），%.1f MB' % (n[0], n[1], os.path.getsize(out) / 1e6))
    db.execute('VACUUM')
    db.close()


if __name__ == '__main__':
    main(*sys.argv[1:4])
