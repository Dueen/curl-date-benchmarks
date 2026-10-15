#!/usr/bin/env python3
"""Native Linux x86-64 runner; no publishing, secrets, caches or paid artifacts.
SPDX-License-Identifier: curl
"""
import csv,hashlib,json,os,pathlib,platform,random,shutil,subprocess,sys
root=pathlib.Path(__file__).resolve().parent
results=root/'results';results.mkdir(exist_ok=True)
source=root/'curl-source';build=root/'curl-build'
base='653f7d7fa983938c4c9331d14c71bc9fa5a5aba8'
assert platform.system()=='Linux' and platform.machine()=='x86_64','Native Linux x86-64 required'
replicate=int(os.environ.get('BENCH_REPLICATE','1'))
cpus=sorted(os.sched_getaffinity(0));os.environ['BENCH_CPU']=str(cpus[0])
commands=[]
def run(name,args,cwd=None,env=None):
 args=[str(x) for x in args];commands.append({'name':name,'args':args,'cwd':str(cwd or root)})
 (results/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')
 print(name,flush=True)
 with (results/(name+'.log')).open('w') as f:
  subprocess.run(args,cwd=cwd or root,env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
metadata={'baseline':base,'replicate':replicate,'system':platform.platform(),'allowed_cpus':cpus,'benchmark_cpu':cpus[0]}
for name,args in [('cpu',['lscpu']),('gcc',[os.environ['CC_GCC'],'--version']),('clang',[os.environ['CC_CLANG'],'--version']),('cmake',['cmake','--version'])]:
 metadata[name]=subprocess.check_output(args,text=True)
(results/'environment.json').write_text(json.dumps(metadata,indent=2)+'\n')
run('clone-curl',['git','clone','--filter=blob:none','--no-checkout','https://github.com/curl/curl.git',source])
run('checkout-curl',['git','checkout','--detach',base],source)
assert (source/'lib/parsedate.c').read_bytes()==(root/'candidates/baseline.c').read_bytes()
(source/'tests/unit/unit4781.c').write_bytes((root/'candidates/unit4781.c').read_bytes())
run('configure',['cmake','-S',source,'-B',build,'-DCMAKE_BUILD_TYPE=Debug','-DENABLE_DEBUG=ON','-DCURL_ENABLE_SSL=OFF','-DCURL_USE_LIBPSL=OFF','-DCURL_USE_LIBSSH2=OFF','-DCURL_USE_LIBIDN2=OFF','-DCURL_BROTLI=OFF','-DCURL_ZSTD=OFF','-DCURL_ZLIB=OFF','-DUSE_NGHTTP2=OFF','-DCURL_DISABLE_LDAP=ON','-DCURL_DISABLE_LDAPS=ON','-DBUILD_SHARED_LIBS=OFF','-DBUILD_STATIC_LIBS=ON','-DBUILD_LIBCURL_DOCS=OFF','-DBUILD_MISC_DOCS=OFF','-DENABLE_CURL_MANUAL=OFF'])
order=['pack2','pack3'];random.Random(replicate).shuffle(order)
(results/'variant-order.json').write_text(json.dumps(order)+'\n')
for variant in ['baseline',*order]:
 (source/'lib/parsedate.c').write_bytes((root/'candidates'/(variant+'.c')).read_bytes())
 run('build-'+variant,['cmake','--build',build,'--target','curl','testdeps','-j','4'])
 run('units-'+variant,['perl',source/'tests/runtests.pl','-a','-n','-j4','unittest'],build/'tests')
 run('dates-'+variant,['perl',source/'tests/runtests.pl','-a','-n','-j4',*map(str,[77,78,247,248,355,420,483,517,762,1104,1126,1127,1128,1415,1424,1511,1549,1596,1668,3103,4781])],build/'tests')
(source/'lib/parsedate.c').write_bytes((root/'candidates/baseline.c').read_bytes())
run('build-baseline-final',['cmake','--build',build,'--target','curl','testdeps','-j','4'])
# All builds/tests complete before any timing starts. Pin timed executables to one allowed CPU.
for variant in order:
 dest=results/variant;dest.mkdir(exist_ok=True)
 for script in ['bench.c','reproduce.py','perf.py','paired-summary.py']:
  shutil.copyfile(root/script,dest/('summarize.py' if script=='paired-summary.py' else script))
 env=os.environ.copy();env['CURL_CANDIDATE_SOURCE']=str(root/'candidates'/(variant+'.c'))
 run(variant+'-sanitize',[sys.executable,dest/'reproduce.py',source,build,'--sanitize'],env=env)
 env_unsigned=env.copy();env_unsigned['EXTRA_CFLAGS']='-funsigned-char'
 run(variant+'-sanitize-unsigned',[sys.executable,dest/'reproduce.py',source,build,'--sanitize'],env=env_unsigned)
 run(variant+'-matrix',[sys.executable,dest/'reproduce.py',source,build],env=env)
 run(variant+'-perf',[sys.executable,dest/'perf.py',source,build],env=env)
 run(variant+'-summary',[sys.executable,dest/'summarize.py'],env=env)
 run(variant+'-assembly',[sys.executable,root/'assembly.py',dest],env=env)
print('All native x86 benchmarks and correctness checks completed.',flush=True)
