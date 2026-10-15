#!/usr/bin/env python3
# Static x86 instruction/branch sites, not hardware counters. SPDX-License-Identifier: curl
import csv,pathlib,re,subprocess,sys
root=pathlib.Path(sys.argv[1]).resolve()
with (root/'assembly.csv').open('w') as out:
 w=csv.writer(out);w.writerow(['compiler','variant','mode','function','instructions','conditional_branches','other_branches','calls','text_bytes'])
 for d in sorted(root.glob('*-O*')):
  for v in ['base','pack']:
   for unit in [False,True]:
    prefix=v+('_unit' if unit else '');obj=d/(prefix+'.o')
    text=subprocess.check_output(['objdump','-d','--no-show-raw-insn',str(obj)],text=True)
    (d/(prefix+'.disasm')).write_text(text)
    syms=subprocess.check_output(['nm','-S','--defined-only',str(obj)],text=True)
    symbols={m[3]:(int(m[1],16),int(m[2],16)) for m in re.finditer(r'^([\da-f]+)\s+([\da-f]+)\s+[tT]\s+(\S+)$',syms,re.M)}
    sizeout=subprocess.check_output(['size','-A',str(obj)],text=True);(d/(prefix+'.size')).write_text(sizeout)
    textbytes=sum(int(m[1]) for m in re.finditer(r'^\.text(?:\.\S+)?\s+(\d+)\s+',sizeout,re.M))
    ins=[(int(m[1],16),m[2]) for m in re.finditer(r'^\s*([\da-f]+):\s+(\S+)',text,re.M)]
    for name in (['checkday','checkmonth','checktz'] if unit else ['ALL']):
     if name=='ALL':ops=[x[1] for x in ins];length=textbytes
     else:
      start,length=symbols[v+('_unit_' if name=='checktz' else '_')+name];ops=[x[1] for x in ins if start<=x[0]<start+length]
     w.writerow([d.name,v,'unit' if unit else 'normal',name,len(ops),sum(x.startswith('j') and x not in ['jmp','jmpq'] or x.startswith('loop') for x in ops),sum(x in ['jmp','jmpq'] for x in ops),sum(x in ['call','callq'] for x in ops),length])
