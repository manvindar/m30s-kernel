#!/usr/bin/env python3
"""Reject source/patch drift before mutation, then exercise actual CPU functions."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from apply_cpu_mali import apply

scripts = Path(__file__).resolve().parent
patches = scripts.parent / 'patches/cpu-mali'
baseline = Path(sys.argv[1]).resolve()
manifest = json.loads((patches / 'manifest.json').read_text())

def source_copy(root):
    for name in manifest['source_pins']:
        dst = root / name
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(baseline / name, dst)

def hashes(root):
    return {name: hashlib.sha256((root/name).read_bytes()).hexdigest()
            for name in manifest['source_pins']}

with tempfile.TemporaryDirectory() as temp:
    temp = Path(temp)
    source = temp / 'src'
    source_copy(source)
    cpu = source / 'kernel/sched/cpufreq_schedutil.c'
    cpu.write_bytes(cpu.read_bytes() + b'\n/* drift */\n')
    before = hashes(source)
    try:
        apply(source, patches)
        raise AssertionError('Source drift accepted')
    except ValueError as exc:
        assert str(exc).startswith('Source drift:')
    assert hashes(source) == before
    source_copy(source)
    bad = temp / 'patches'
    shutil.copytree(patches, bad)
    patch = bad / sorted(manifest['patch_sha256'])[0]
    patch.write_bytes(patch.read_bytes() + b'\n')
    before = hashes(source)
    try:
        apply(source, bad)
        raise AssertionError('Patch drift accepted')
    except ValueError as exc:
        assert str(exc).startswith('Patch drift:')
    assert hashes(source) == before
    red = subprocess.run([sys.executable, str(scripts/'run_schedutil_cache_regression.py'),
                          str(cpu), str(temp/'red')], capture_output=True, text=True)
    assert red.returncode == 1, red.stdout + red.stderr
    scenarios = json.loads(red.stdout)
    assert len(scenarios) == 2 and all(x['exit'] == 1 and 'after rate-limit expiry' in x['stderr'] for x in scenarios)
    apply(source, patches)
    subprocess.run([sys.executable, str(scripts/'run_schedutil_cache_regression.py'),
                    str(cpu), str(temp/'green')], check=True)
    before = hashes(source)
    try:
        apply(source, patches)
        raise AssertionError('Duplicate application accepted')
    except ValueError as exc:
        assert str(exc).startswith('Source drift:')
    assert hashes(source) == before
print('PASS: source drift, patch drift, duplicate rejection; actual CPU up/down red→green')
