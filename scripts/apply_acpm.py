#!/usr/bin/env python3
"""Apply the exact reviewed nine-access ACPM fix; reject source or patch drift."""
import hashlib, json, subprocess, sys
from pathlib import Path
root = Path(sys.argv[1]); patch = Path(sys.argv[2]).resolve()
source = root / 'drivers/soc/samsung/acpm/acpm_ipc.c'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
before = sha(source)
assert before == '2207913f7371365eb7e98fcbad5031832498bb37ea01052c1359554062a096e9', 'ACPM source drift'
assert sha(patch) == '28b3a83b5514eb6bff9c61d094ef10e54cdbb6796bd6e8bdbfc56a845b30eb78', 'ACPM patch drift'
subprocess.run(['patch', '--batch', '--fuzz=0', '-p1', '-i', str(patch)], cwd=root, check=True, capture_output=True)
after = sha(source)
assert after == 'd6b9218df5dd2ff47ceee4fd27e2633db0b8e0638bba704b991d8167dada32ed', 'ACPM patched source mismatch'
print(json.dumps({'before_sha256': before, 'after_sha256': after, 'patch_sha256': sha(patch), 'read_sites': 4, 'write_sites': 5, 'runtime_verified': False}, indent=2))
