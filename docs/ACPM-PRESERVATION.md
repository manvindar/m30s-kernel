# ACPM fixed-kernel preservation candidate

This change preserves the existing PSI, CPU/Mali, boost and performance-profile build paths and changes exactly nine ACPM inform memory-mapped I/O accesses: four reads and five clears. The input and patched source hashes must match the retained fully built repair. The cloud workflow runs the pinned clang regression and checks the actual compiled kernel object for 32-bit accesses. It retains source, object, config, image and boot receipts. These checks do not prove runtime stability or byte identity to the historical kernel.

Reproduce using `fragment=true`, `perf=false`, `boost=false`, `hdr=false`, `performance_profile=true`, `cpu_mali=true`, `version_date=20261110`, `publish=false`. Compare the full resulting config with retained SHA256 `bca7402de04ffc2bdd281ef09e73db57af49248e244fa382ee5b8a8b98e0a6b7` before acceptance; verify inherited source receipts and independent boot reconstruction. No device write is part of this build.

Until reviewed cloud output is available, prefer a system-only ROM upgrade retaining a freshly matched installed fixed boot. Do not replace that boot with the older dated profile1 image.
