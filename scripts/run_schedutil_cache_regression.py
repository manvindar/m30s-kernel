#!/usr/bin/env python3
"""Compile actual schedutil functions; mock only unavailable kernel/CPU hardware boundaries."""
import pathlib,re,subprocess,sys,json
root=pathlib.Path(__file__).resolve().parent
source=pathlib.Path(sys.argv[1]); output=pathlib.Path(sys.argv[2]);output.mkdir(parents=True,exist_ok=True)
text=source.read_text()
def extract(name):
 m=re.search(r"static\s+(?:bool|unsigned int|void)\s+"+name+r"\s*\(",text)
 assert m,name
 start=m.start();brace=text.index("{",m.end());depth=1;i=brace+1
 while depth:
  depth += (text[i]=="{")-(text[i]=="}");i+=1
 return text[start:i]
functions="\n".join(extract(n) for n in ["sugov_up_down_rate_limit","sugov_update_commit","get_next_freq"])
c=(root/"test_schedutil_cache.c.in").read_text().replace("/* EXTRACTED_KERNEL_FUNCTIONS */",functions)
(output/"regression.c").write_text(c)
p=subprocess.run(["cc","-std=gnu11","-Werror=implicit-function-declaration",str(output/"regression.c"),"-o",str(output/"regression")],capture_output=True,text=True)
if p.returncode:print(p.stderr);sys.exit(2)
results=[]
for scenario in ["up","down"]:
 p=subprocess.run([str(output/"regression"),scenario],capture_output=True,text=True)
 results.append(dict(scenario=scenario,exit=p.returncode,stdout=p.stdout,stderr=p.stderr))
print(json.dumps(results,indent=2));sys.exit(any(x["exit"] for x in results))
