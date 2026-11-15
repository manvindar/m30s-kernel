#!/usr/bin/env python3
"""Compile extracted actual ACPM function/struct and ARM64 raw I/O accessors.
This isolates the code-width regression, not the full kernel build/ABI.
"""
import argparse, hashlib, json, re, subprocess
from pathlib import Path

def block(text, marker):
    start=text.index(marker); brace=text.index('{',start);depth=1;end=brace+1
    while depth:
        depth += (text[end]=='{')-(text[end]=='}');end+=1
    return text[start:end]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--clang',required=True);ap.add_argument('--objdump',required=True);ap.add_argument('--inputs',default=str(Path(__file__).parent));ap.add_argument('--out',required=True);args=ap.parse_args()
    src=Path(args.inputs);out=Path(args.out);out.mkdir(parents=True,exist_ok=False)
    expected={'acpm_ipc.fixed.c':'d6b9218df5dd2ff47ceee4fd27e2633db0b8e0638bba704b991d8167dada32ed','acpm_ipc.c':'2207913f7371365eb7e98fcbad5031832498bb37ea01052c1359554062a096e9','framework.h':'4dded173cae532110cb68a09abd6ac1a5f716d3ab559abf798e928ec2511571f','common.h':'6ab37ea84bd277b7938845165cc25cecdd1e0c5e8122a5637ec3da5a2c36334c','io.h':'4832586f899e7c2022f5361bee4df481d24034d0448056317fb524634819ecbb'}
    for n,h in expected.items():
        assert hashlib.sha256((src/n).read_bytes()).hexdigest()==h, 'input drift: '+n
    io=(src/'io.h').read_text();framework=block((src/'framework.h').read_text(),'struct acpm_framework {')+';'
    common=(src/'common.h').read_text();build=block(common,'struct build_info {')+';'
    access='\n'.join(block(io,m) for m in ['static inline void __raw_writel(', 'static inline u32 __raw_readl('])
    prefix='''typedef unsigned int u32;
typedef unsigned long size_t;
#define CONFIG_EXYNOS_ACPM 1
#define __iomem
#define BUILDINFO_ELEMENT_SIZE 24
#define dbg_snapshot_reg(a,b,c,d) do {} while(0)
#define ALTERNATIVE(a,b,c) a
extern int printk(const char *, ...);
#define pr_info(fmt, ...) printk("\\0016" fmt, ##__VA_ARGS__)
'''+build+'\n'+framework+'\n_Static_assert(__builtin_offsetof(struct acpm_framework, inform_head)==156, "head layout");\n_Static_assert(__builtin_offsetof(struct acpm_framework, inform0)==160, "array0 layout");\n_Static_assert(__builtin_offsetof(struct acpm_framework, inform3)==232, "array3 layout");\n'+access+'\nstruct acpm_framework *acpm_initdata;\n'
    results={}
    for label,name in [('baseline','acpm_ipc.c'),('fixed','acpm_ipc.fixed.c')]:
        fun=block((src/name).read_text(),'void acpm_get_inform(void)')
        c=out/(label+'.c');obj=out/(label+'.o');c.write_text(prefix+fun+'\n')
        cmd=[args.clang,'--target=aarch64-linux-gnu','-O2','-ffreestanding','-fno-builtin','-fno-strict-aliasing','-fno-vectorize','-fno-slp-vectorize','-mgeneral-regs-only','-c',str(c),'-o',str(obj)]
        subprocess.run(cmd,check=True,capture_output=True)
        dis=subprocess.run([args.objdump,'-d',str(obj)],check=True,capture_output=True,text=True).stdout
        (out/(label+'.disassembly.txt')).write_text(dis)
        # General-regs-only excludes vector accesses. Stack saves may use64-bit stores.
        # All non-stack stores in this isolated function are ACPM clears.
        stores=[line for line in dis.splitlines() if re.search(r'\b(?:str|stur|stp)\b',line) and not re.search(r'\[(?:sp|x29)(?:,|\])',line)]
        wide=[line for line in stores if re.search(r'\b(?:str|stur|stp)\s+x',line)]
        narrow=[line for line in stores if re.search(r'\b(?:str|stur)\s+w',line)]
        results[label]={'stores':stores,'wide_nonstack_stores':wide,'narrow_nonstack_stores':narrow,'command':cmd}
    assert results['baseline']['wide_nonstack_stores'], 'RED not reproduced: baseline did not widen stores'
    assert not results['fixed']['wide_nonstack_stores'], 'fixed still widens mapped writes'
    assert len(results['fixed']['narrow_nonstack_stores'])>=5, 'fixed missing explicit write sites (compiler may retain six-iteration loop)'
    versions={k:subprocess.run([v,'--version'],check=True,capture_output=True,text=True).stdout for k,v in [('clang',args.clang),('objdump',args.objdump)]}
    pins={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in src.iterdir() if p.name in ['acpm_ipc.c','acpm_ipc.fixed.c','framework.h','common.h','io.h','run_acpm_regression.py']}
    receipt={'result':'PASS: baseline unsafe-wide-store RED / explicit32-bit fixed GREEN','results':results,'versions':versions,'inputs':pins,'limits':['Extracted actual function/struct/accessor test, not full kernel compile','Debug-snapshot reg macro disabled matching shipped config','ALTERNATIVE expansion selects base ldr; both source alternative operands are32-bit','Native pinned clang4639204 and full config build remain CI gates']}
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['result'])
if __name__=='__main__':main()
