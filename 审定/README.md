# 审定文件

把词汇表页面"审定"页导出的 .json 文件放在这个文件夹里，然后告诉编者（Claude）。

应用方法（编者执行）：

```sh
cd _work
python3 -I scripts/akbh1_apply_review.py align/akbh1 ../审定/审定-界品-某某-20261101-1030.json --dry   # 先试算
python3 -I scripts/akbh1_apply_review.py align/akbh1 ../审定/审定-界品-某某-20261101-1030.json
python3 -I scripts/akbh1_verify.py align/akbh1
.venv/bin/python scripts/pkg_build.py   # 重新生成资料包
```

多人的审定文件可以一次传入；意见不一致、或审定之后数据又改过的条目不会自动套用，会列在日志 `_work/align/akbh1/review_log.md` 里。
