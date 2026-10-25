#!/usr/bin/env python3
"""Build and verify a deterministic runtime-only skill ZIP from an allowlist."""
import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path, PurePosixPath
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[2]


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def payload(root=ROOT):
    config=json.loads((root/'release/manifest.json').read_text(encoding='utf-8'))
    if not re.fullmatch(r'\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?',config['version']):
        raise ValueError('Invalid release version')
    source=(root/config['source_directory']).resolve()
    if not source.is_relative_to(root.resolve()):raise ValueError('Source outside repository')
    expected=config['files']
    if len(expected)!=len(set(expected)):raise ValueError('Duplicate manifest entry')
    actual={p.relative_to(source).as_posix() for p in source.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    if actual != set(expected):
        raise ValueError(f'Runtime tree differs from allowlist: extra={actual-set(expected)}, missing={set(expected)-actual}')
    contents={}
    for name in expected:
        path=PurePosixPath(name)
        if path.is_absolute() or '..' in path.parts:raise ValueError('Unsafe member path')
        file=source/name
        if file.is_symlink() or not file.resolve().is_relative_to(source):raise ValueError('Unsafe runtime file')
        data=file.read_bytes()
        if re.search(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\bgh[pousr]_[A-Za-z0-9]{20,}|\bgithub_pat_[A-Za-z0-9_]{20,}',data):
            raise ValueError('Credential marker in runtime payload: '+name)
        contents[name]=data
    # Product references must resolve inside the actual package, not the repository.
    for name,data in contents.items():
        if not name.endswith('.md'):continue
        for target in re.findall(r'\]\(([^)]+)\)',data.decode('utf-8')):
            if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:',target) or target.startswith('#'):continue
            linked=(source/PurePosixPath(name).parent/unquote(target.split('#')[0])).resolve()
            if not linked.is_relative_to(source) or linked.relative_to(source).as_posix() not in contents:
                raise ValueError(f'Unbundled runtime reference: {name} -> {target}')
    return config,contents


def build(output_dir,root=ROOT):
    config,contents=payload(root)
    records={name:dict(sha256=sha256(data),bytes=len(data)) for name,data in sorted(contents.items())}
    fingerprint=sha256(json.dumps(records,sort_keys=True,separators=(',',':')).encode())
    package=dict(version=config['version'],channel=config['channel'],skill_name=config['skill_name'],
                 runtime_fingerprint_sha256=fingerprint,files=records,
                 excluded=['tests','tools','docs','data','legacy','local logs','credentials'])
    contents['VERSION']=(config['version']+'\n').encode()
    contents['PACKAGE_MANIFEST.json']=(json.dumps(package,sort_keys=True,indent=2)+'\n').encode()
    out=Path(output_dir);out.mkdir(parents=True,exist_ok=True)
    archive=out/f"{config['skill_name']}-{config['version']}.zip"
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,data in sorted(contents.items()):
            info=zipfile.ZipInfo(config['archive_prefix']+'/'+name,date_time=(2020,1,1,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
            z.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None:raise ValueError('ZIP integrity failure')
        if len(z.namelist())!=len(contents):raise ValueError('ZIP member count mismatch')
        for name,data in contents.items():
            if z.read(config['archive_prefix']+'/'+name)!=data:raise ValueError('ZIP byte mismatch')
    checksum=sha256(archive.read_bytes())
    (out/'SHA256SUMS.txt').write_text(checksum+'  '+archive.name+'\n',encoding='ascii')
    (out/'release-manifest.json').write_text(json.dumps(dict(package,archive=archive.name,
        archive_sha256=checksum,archive_bytes=archive.stat().st_size,archive_files=len(contents)),indent=2)+'\n',encoding='utf-8')
    return archive


def main():
    p=argparse.ArgumentParser();p.add_argument('--output-dir',default=str(ROOT/'dist'));a=p.parse_args()
    archive=build(a.output_dir)
    print(json.dumps(dict(archive=str(archive),sha256=sha256(archive.read_bytes()))))


if __name__=='__main__':main()
