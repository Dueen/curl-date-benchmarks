#!/usr/bin/env python3
# Job logs/summary do not consume Actions artifact storage. SPDX-License-Identifier: curl
import base64,csv,hashlib,io,os,pathlib,tarfile
root=pathlib.Path(__file__).resolve().parent
results=root/'results';results.mkdir(exist_ok=True)
lines=['### Native x86 paired latency changes','', '| Candidate | Compiler | Curl perf | Random corpus | Valid months | Valid weekdays |','|---|---|---:|---:|---:|---:|']
for candidate in ['pack2','pack3']:
 f=results/candidate/'summary.csv'
 if not f.exists():continue
 rows=list(csv.DictReader(f.open()));lookup={(x['compiler'],x['workload']):x for x in rows}
 for compiler in ['clang-O2','clang-O3','gcc-O2','gcc-O3']:
  keys=['curl-original-perf','parser-corpus-random','month-valid','day-valid']
  if not all((compiler,k) in lookup for k in keys):continue
  lines.append('| '+candidate+' | '+compiler+' | '+' | '.join(f"{float(lookup[compiler,k]['paired_median_delta_pct']):+.2f}%" for k in keys)+' |')
lines+=['','Negative means faster. Hosted VMs can be noisy; compare all three replicates and CPU metadata. Raw evidence is encoded in this job log. No paid runner, cache or artifact upload is used.']
summary='\n'.join(lines)+'\n';print(summary,flush=True)
(results/'summary.md').write_text(summary)
if os.environ.get('GITHUB_STEP_SUMMARY'):
 with open(os.environ['GITHUB_STEP_SUMMARY'],'a') as f:f.write(summary)
files=[p for p in results.rglob('*') if p.is_file() and p.suffix in ['.c','.h','.py','.csv','.s','.disasm','.size','.txt','.json','.md','.log']]
manifest=''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(results))+'\n' for p in sorted(files))
(results/'MANIFEST.sha256').write_text(manifest)
buf=io.BytesIO()
with tarfile.open(fileobj=buf,mode='w:gz') as t:
 for p in files+[results/'MANIFEST.sha256']:t.add(p,arcname=str(p.relative_to(results)))
data=buf.getvalue();print('BENCHMARK_BUNDLE_SHA256 '+hashlib.sha256(data).hexdigest(),flush=True)
print('BENCHMARK_BUNDLE_BEGIN',flush=True)
print(base64.encodebytes(data).decode('ascii'),end='',flush=True)
print('BENCHMARK_BUNDLE_END',flush=True)
