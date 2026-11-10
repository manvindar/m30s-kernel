#!/usr/bin/env python3
"""Apply the four-file candidate only to its reviewed source and patch identities."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def apply(source, patch_dir):
    source = Path(source).resolve()
    patch_dir = Path(patch_dir).resolve()
    manifest = json.loads((patch_dir / 'manifest.json').read_text())
    for name, pins in manifest['source_pins'].items():
        if digest(source / name) != pins['before']:
            raise ValueError('Source drift: ' + name)
    for name, pin in manifest['patch_sha256'].items():
        if digest(patch_dir / name) != pin:
            raise ValueError('Patch drift: ' + name)
    env = os.environ.copy()
    # Prevent Git discovering the enclosing Actions checkout and skipping src paths.
    env['GIT_CEILING_DIRECTORIES'] = str(source.parent)
    for key in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE'):
        env.pop(key, None)
    patches = [str(patch_dir / name) for name in sorted(manifest['patch_sha256'])]
    subprocess.run(['git', 'apply', '--check', '--verbose', *patches], cwd=source, env=env, check=True)
    subprocess.run(['git', 'apply', '--verbose', *patches], cwd=source, env=env, check=True)
    actual = {}
    for name, pins in manifest['source_pins'].items():
        actual[name] = digest(source / name)
        if actual[name] != pins['after']:
            raise ValueError('Applied source mismatch: ' + name)
    return dict(donor_sha=manifest['donor_sha'], source_after_sha256=actual,
                patch_sha256=manifest['patch_sha256'], native_compile_verified=False,
                runtime_verified=False)


if __name__ == '__main__':
    print(json.dumps(apply(sys.argv[1], sys.argv[2]), indent=2))
