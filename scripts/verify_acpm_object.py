#!/usr/bin/env python3
"""Verify actual compiled ACPM function access widths; record reproducible pins."""
import hashlib, json, re, subprocess, sys
from pathlib import Path
root=Path(sys.argv[1]); objdump=sys.argv[2]; out=Path(sys.argv[3]); out.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=root/'drivers/soc/samsung/acpm/acpm_ipc.c'; obj=source.with_suffix('.o')
assert sha(source)=='d6b9218df5dd2ff47ceee4fd27e2633db0b8e0638bba704b991d8167dada32ed'
dis=subprocess.run([objdump,'-d',str(obj)],check=True,capture_output=True,text=True).stdout
match=re.search(r'^[0-9a-f]+ <acpm_get_inform>:\n(.*?)(?=^[0-9a-f]+ <|\Z)',dis,re.M|re.S)
assert match, 'Missing actual ACPM function'
fun=match.group(0); stores=[line for line in fun.splitlines() if re.search(r'\b(?:str|stur|stp)\b',line) and not re.search(r'\[(?:sp|x29)(?:,|\])',line)]
assert len(stores)>=5 and all(re.search(r'\b(?:str|stur)\s+w',line) for line in stores), stores
assert re.search(r'\bldr\s+w',fun), 'Missing 32-bit reads'
assert not re.search(r'\b(?:ldr|str|ldp|stp)\s+[qds]',fun), 'Vector SRAM access'
(out/'actual-function.txt').write_text(fun)
receipt={'source_sha256':sha(source),'object_sha256':sha(obj),'kernel_sha256':sha(root/'arch/arm64/boot/Image'),'config_sha256':sha(root/'.config'),'stores':stores,'runtime_verified':False}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
