#!/usr/bin/env python3
# Decode one job log, check hashes and reject unsafe paths. SPDX-License-Identifier: curl
import base64,hashlib,io,pathlib,re,sys,tarfile
lines=pathlib.Path(sys.argv[1]).read_text().splitlines()
begin=next(i for i,s in enumerate(lines) if s.rstrip().endswith('BENCHMARK_BUNDLE_BEGIN'))
end=next(i for i,s in enumerate(lines[begin+1:],begin+1) if s.rstrip().endswith('BENCHMARK_BUNDLE_END'))
expected=next(re.search(r'BENCHMARK_BUNDLE_SHA256 ([0-9a-f]{64})',s)[1] for s in lines[:begin] if 'BENCHMARK_BUNDLE_SHA256 ' in s)
# gh prefixes log lines with job/step names and timestamp; encoded payload is the last whitespace-delimited field.
encoded=''.join(s.split()[-1] for s in lines[begin+1:end] if s.strip())
data=base64.b64decode(encoded,validate=True)
assert hashlib.sha256(data).hexdigest()==expected,'Bundle hash mismatch'
out=pathlib.Path(sys.argv[2]).absolute()
assert not out.exists() and not out.is_symlink(),'Output directory must be new'
out=out.resolve()
with tarfile.open(fileobj=io.BytesIO(data),mode='r:gz') as archive:
 members=archive.getmembers();blobs={}
 for member in members:
  path=pathlib.PurePosixPath(member.name)
  assert member.isfile() and path.parts and not path.is_absolute() and '..' not in path.parts,'Unsafe archive entry'
  assert member.name not in blobs,'Duplicate archive entry'
  blobs[member.name]=archive.extractfile(member).read()
 manifest=blobs['MANIFEST.sha256'].decode()
 checked=set()
 for line in manifest.splitlines():
  digest,name=line.split('  ',1)
  assert name in blobs and hashlib.sha256(blobs[name]).hexdigest()==digest,'File hash mismatch'
  checked.add(name)
 assert checked|{'MANIFEST.sha256'}==set(blobs),'Unmanifested file'
 out.mkdir(parents=True,exist_ok=False)
 for name,blob in blobs.items():
  target=out/name;target.parent.mkdir(parents=True,exist_ok=True)
  with target.open('xb') as f: f.write(blob)
print(f'Verified and extracted {len(blobs)} files into {out}')
