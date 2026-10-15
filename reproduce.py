#!/usr/bin/env python3
"""Build unchanged current curl sources, renamed baseline/candidate symbols, no LTO.
Usage: python3 reproduce.py SOURCE CONFIG_BUILD [--sanitize] [--compile-only]
Compiler matrix defaults to Apple clang / Homebrew GCC, O2 and O3.
SPDX-License-Identifier: curl
"""
import os, pathlib, re, subprocess, sys, shlex
root=pathlib.Path(__file__).resolve().parent
src=pathlib.Path(sys.argv[1]).resolve(); build=pathlib.Path(sys.argv[2]).resolve()
sanitize='--sanitize' in sys.argv
base_ref=os.environ.get('CURL_BASE_REF','653f7d7fa983938c4c9331d14c71bc9fa5a5aba8')
baseline=subprocess.check_output(['git','-C',str(src),'show',base_ref+':lib/parsedate.c'])
baseline_path=root/'baseline-parsedate.c'
if baseline_path.exists() and baseline_path.read_bytes()!=baseline:
 raise RuntimeError('Existing baseline differs from '+base_ref)
baseline_path.write_bytes(baseline)
compilers=[('clang',os.environ.get('CC_CLANG','clang-17')),('gcc',os.environ.get('CC_GCC','gcc-14'))]
if sanitize: compilers=compilers[:1]
corpus=(src/'tests/perf/dateparser.c').read_text().split('static const char *dates[] = {',1)[1].split('\n};',1)[0]
(root/'corpus.h').write_text('/* Exact curl tests/perf/dateparser.c corpus. */\nstatic const char *corpus[] = {'+corpus+'\n};\n')
candidate_path=pathlib.Path(os.environ.get('CURL_CANDIDATE_SOURCE',str(root/'two-byte-parsedate.c')))
(root/'packed-parsedate.c').write_bytes(candidate_path.read_bytes())
def run(args,**kw):
    args=[str(a) for a in args]
    if os.environ.get('BENCH_CPU') and pathlib.Path(args[0]).name=='bench': args=['taskset','-c',os.environ['BENCH_CPU'],*args]
    subprocess.run(args,check=True,**kw)
for label,cc in compilers:
 for opt in ([1] if sanitize else [2,3]):
  tag=('sanitize-unsigned-char' if '-funsigned-char' in shlex.split(os.environ.get('EXTRA_CFLAGS','')) else 'sanitize') if sanitize else f'{label}-O{opt}'
  dest=root/tag;dest.mkdir(exist_ok=True)
  flags=[f'-O{opt}','-g','-DHAVE_CONFIG_H','-DBUILDING_LIBCURL','-DCURL_STATICLIB',f'-I{build}/lib',f'-I{src}/lib',f'-I{src}/include']
  flags+=shlex.split(os.environ.get('EXTRA_CFLAGS',''))
  if sanitize: flags+=['-fsanitize=address,undefined','-fno-omit-frame-pointer']
  objects=[]
  for name in ['baseline-parsedate.c','packed-parsedate.c']:
   run([cc,*flags,'-DCURL_DISABLE_PARSEDATE','-c',root/name,'-o',dest/(name+'.disabled.o')])
  for variant in ['base','pack']:
   source=root/('baseline-parsedate.c' if variant=='base' else 'packed-parsedate.c')
   for unit in [False,True]:
    prefix=variant+('_unit' if unit else '')
    names=['Curl_wkday','Curl_month','curl_getdate','Curl_getdate_capped','checkday','checkmonth','checktz']
    defs=[f'-D{n}={prefix}_{n}' for n in names]
    if unit:
     defs+=['-DUNITTESTS','-Dcheckday='+variant+'_checkday','-Dcheckmonth='+variant+'_checkmonth']
     # Replace rather than redefine lookup names.
     defs=[x for x in defs if x not in [f'-Dcheckday={prefix}_checkday',f'-Dcheckmonth={prefix}_checkmonth']]
    obj=dest/(prefix+'.o');objects.append(obj)
    run([cc,*flags,*defs,'-c',source,'-o',obj])
    if not sanitize:
     with (dest/(prefix+'.s')).open('w') as f: run([cc,*flags,*defs,'-S',source,'-o','-'],stdout=f)
  for f in ['curlx/strparse.c','strcase.c','strequal.c']:
   obj=dest/(pathlib.Path(f).stem+'.o');objects.append(obj)
   run([cc,*flags,'-c',src/'lib'/f,'-o',obj])
  exe=dest/'bench'
  run([cc,*flags,root/'bench.c',*objects,'-o',exe])
  with (dest/'verify.txt').open('w') as out: run([exe,'verify'],stdout=out)
  print(tag,(dest/'verify.txt').read_text().strip(),flush=True)
  if not sanitize and '--compile-only' not in sys.argv:
   with (dest/'raw.csv').open('w') as out: run([exe],stdout=out)
   print(tag,'benchmarked',flush=True)
