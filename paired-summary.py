#!/usr/bin/env python3
"""Summarize paired samples; negative delta means faster. SPDX-License-Identifier: curl"""
import csv,pathlib,random,statistics
root=pathlib.Path(__file__).resolve().parent
rng=random.Random(4781)
def stats(rows):
 b=[float(x['base_ns']) for x in rows];p=[float(x['packed_ns']) for x in rows]
 ratios=[y/x for x,y in zip(b,p)]
 boot=sorted(statistics.median(rng.choices(ratios,k=len(ratios))) for _ in range(10000))
 return [len(rows),statistics.median(b),statistics.median(p),100*(statistics.median(ratios)-1),100*(boot[250]-1),100*(boot[9749]-1)]
with (root/'summary.csv').open('w') as out:
 w=csv.writer(out);w.writerow(['compiler','workload','pairs','base_median_ns','packed_median_ns','paired_median_delta_pct','bootstrap_low_pct','bootstrap_high_pct'])
 for d in sorted(root.glob('*-O*')):
  rows=list(csv.DictReader((d/'raw.csv').open()))
  for name in sorted({x['workload'] for x in rows}): w.writerow([d.name,name,*stats([x for x in rows if x['workload']==name])])
  rows=list(csv.DictReader((d/'perf.csv').open()));w.writerow([d.name,'curl-original-perf',*stats(rows)])
print((root/'summary.csv').read_text())
