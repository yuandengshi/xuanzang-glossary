#!/usr/bin/env python3
"""akbh1_apply_review.py -- 把词汇表页面导出的审定结果（.json）应用到对应实例数据。

Usage: python3 -I akbh1_apply_review.py AKBH1_DIR REVIEW.json [REVIEW2.json ...] [--dry]
规则：
  同意：note 中的"待核"改为"已审定"，并记审定人、日期、说明；
  改正：按审定填写的内容改 lemma / xz / type，note 中保留原写法与说明；
  存疑：保留"待核"，记下意见；
  核对：审定时的原值（orig）与当前数据不符的（数据其后改过），不自动套用，列出交编者处理；
  多人对同一条意见不一致的，不自动套用，列出交编者裁定。
结果：改写 occ/*.tsv（--dry 时只报告），日志追加到 AKBH1_DIR/review_log.md。改正后请再跑 akbh1_verify.py。
审定文件可以同时含几品的条目（页面导出的是全书一份）：只处理属于 AKBH1_DIR 的单位，其余各品请对相应目录再运行一次。
"""
import csv
import datetime
import glob
import json
import os
import sys


def main(d, files, dry):
    items = {}
    for f in files:
        x = json.load(open(f, encoding='utf-8'))
        if x.get('format') != 'xzg-review':
            sys.exit('%s 不是审定结果文件' % f)
        for it in x['items']:
            it = dict(it, reviewer=it.get('reviewer') or x.get('reviewer') or '未署名', file=os.path.basename(f))
            items.setdefault(it['oid'], []).append(it)
    occ = {}
    for f in sorted(glob.glob(os.path.join(d, 'occ', 'U*.tsv'))):
        hdr = open(f, encoding='utf-8').readline().rstrip('\n').split('\t')
        rows = list(csv.DictReader(open(f, encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE))
        occ[f] = (hdr, rows)
    where = {r['oid']: r for _, (h, rows) in occ.items() for r in rows}
    mine = {os.path.basename(f)[:-4] for f in occ}
    other = [o for o in items if o.split('-')[0] not in mine]   # 属于其他品的条目
    for o in other:
        del items[o]
    log, done, skip = [], 0, 0
    key = lambda it: (it['verdict'], it.get('lemma'), it.get('xz'), it.get('type')) if it['verdict'] == '改正' else (it['verdict'],)
    for oid, its in sorted(items.items()):
        r = where.get(oid)
        if not r:
            log.append('- %s：当前数据中找不到，跳过' % oid); skip += 1; continue
        if len({key(i) for i in its}) > 1:
            log.append('- %s：审定意见不一致，未套用——%s' % (oid, '；'.join('%s %s%s' % (
                i['reviewer'], i['verdict'], '（%s/%s/%s）' % (i.get('lemma'), i.get('xz'), i.get('type')) if i['verdict'] == '改正' else '')
                for i in its)))
            skip += 1; continue
        it = max(its, key=lambda i: i.get('ts', 0))
        o = it.get('orig', {})
        if o and (o.get('lemma'), o.get('xz'), o.get('type')) != (r['lemma'], r['xz'], r['type']):
            log.append('- %s：审定之后数据已改（审定时 %s/%s/%s，现在 %s/%s/%s），未套用' % (
                oid, o.get('lemma'), o.get('xz'), o.get('type'), r['lemma'], r['xz'], r['type']))
            skip += 1; continue
        date = datetime.datetime.fromtimestamp(it.get('ts', 0) / 1000).date().isoformat() if it.get('ts') else ''
        who = '、'.join(sorted({i['reviewer'] for i in its}))
        cm = ('；' + it['comment']) if it.get('comment') else ''
        if it['verdict'] == '同意':
            r['note'] = (r['note'].replace('待核', '已审定') + ' 〔审定：同意（%s %s）%s〕' % (who, date, cm)).strip()
        elif it['verdict'] == '改正':
            before = '%s / %s / %s' % (r['lemma'] or '—', r['xz'] or '—', r['type'])
            for k in ('lemma', 'xz', 'type'):
                if it.get(k) is not None:
                    r[k] = it[k]
            r['note'] = (r['note'].replace('待核', '已审定') + ' 〔审定改正（%s %s）：原作 %s%s〕' % (who, date, before, cm)).strip()
        elif it['verdict'] == '存疑':
            r['note'] = (r['note'] + ' 〔审定存疑（%s %s）%s〕' % (who, date, cm)).strip()
        log.append('- %s：%s（%s）%s' % (oid, it['verdict'], who, cm))
        done += 1
    if not dry:
        for f, (hdr, rows) in occ.items():
            with open(f, 'w', encoding='utf-8') as fo:
                fo.write('\t'.join(hdr) + '\n')
                for r in rows:
                    fo.write('\t'.join(r[h] for h in hdr) + '\n')
        with open(os.path.join(d, 'review_log.md'), 'a', encoding='utf-8') as fo:
            fo.write('\n## %s 应用审定：%s\n\n' % (datetime.date.today().isoformat(), '、'.join(os.path.basename(f) for f in files)))
            fo.write('\n'.join(log) + '\n')
    print('\n'.join(log))
    print('%s套用 %d 条，未套用 %d 条%s' % ('（试算）' if dry else '', done, skip,
          '；另有 %d 条属于其他品，请对相应目录再运行' % len(other) if other else ''))


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if a != '--dry']
    main(args[0], args[1:], '--dry' in sys.argv)
