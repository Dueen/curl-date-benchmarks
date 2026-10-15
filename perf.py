#!/usr/bin/env python3
"""Run curl's unmodified perf/dateparser.c in its original corpus order.
Renames only curl_getdate; links optimized parser dependencies from reproduce.py.
The debug library supplies formatting and clock helpers outside the timed hot path.
SPDX-License-Identifier: curl
"""
import csv,pathlib,random,re,subprocess,sys,shlex,os
root=pathlib.Path(__file__).resolve().parent
src=pathlib.Path(sys.argv[1]).resolve();build=pathlib.Path(sys.argv[2]).resolve()
ccs={'clang':os.environ.get('CC_CLANG','clang-17'),'gcc':os.environ.get('CC_GCC','gcc-14')}
(root/'perf-main.c').write_text('#include "'+str(src/'tests/perf/dateparser.c')+'"\nint main(int argc, char **argv) { return test_dateparser(argc, (const char **)argv); }\n')
rng=random.Random(22981)
archive=next(p for p in [build/'lib/libcurl-d.a',build/'lib/libcurl.a'] if p.exists())
link=shlex.split((build/'tests/perf/CMakeFiles/perf.dir/link.txt').read_text())
libindex=next(i for i,x in enumerate(link) if 'libcurl-d.a' in x or 'libcurl.a' in x)
linkflags=[x for x in link[:libindex] if x.startswith('-L') or x.startswith('-Wl,-rpath')]+link[libindex+1:]
for tag in ['clang-O2','clang-O3','gcc-O2','gcc-O3']:
 d=root/tag;cc=ccs[tag.split('-')[0]];opt=tag[-1]
 for v in ['base','pack']:
  subprocess.run([cc,'-O'+opt,'-DHAVE_CONFIG_H','-DBUILDING_LIBCURL','-DCURL_STATICLIB','-Dcurl_getdate='+v+'_curl_getdate','-I'+str(build/'lib'),'-I'+str(src/'lib'),'-I'+str(src/'include'),'-I'+str(src/'tests/perf'),str(root/'perf-main.c'),str(d/(v+'.o')),*[str(d/(s+'.o')) for s in ['strparse','strcase','strequal']],str(archive),*linkflags,'-o',str(d/(v+'-perf'))],check=True)
 with (d/'perf.csv').open('w') as f:
  out=csv.writer(f);out.writerow(['round','first','base_ns','packed_ns','base_errors','packed_errors'])
  for r in range(15):
   order=['base','pack'];rng.shuffle(order);data={}
   for v in order:
    command=[str(d/(v+'-perf')),'20000']
    if os.environ.get('BENCH_CPU'): command=['taskset','-c',os.environ['BENCH_CPU'],*command]
    raw=subprocess.check_output(command,text=True)
    (d/(v+'-perf-last.txt')).write_text(raw)
    data[v]=(re.search(r'Time/date:\s+([\d.]+)',raw)[1],re.search(r'Errors:\s+(\d+)',raw)[1])
   out.writerow([r,order[0],data['base'][0],data['pack'][0],data['base'][1],data['pack'][1]])
 print(tag,'original curl perf benchmark complete',flush=True)
