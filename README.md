# Kernel for the Samsung Galaxy M30s (SM-M307F)

Builds Samsung's official open-source kernel (Linux 4.14.113, `exynos9610-m30sdd_defconfig`, Android 11 drop `SM-M307F_SWA_RR`) on GitHub Actions. Mac is too small for it.

- `Kernel.tar.gz` (181 MB, over git's file limit) is a release asset named `source-SM-M307F_SWA_RR`; the workflow downloads it. Private repo: Samsung's GPL source, keep it private unless decided otherwise.
- Toolchains are Samsung's: AOSP `clang-4639204` and gcc 4.9 from tag `android-9.0.0_r30`.
- Run `Build kernel` from the Actions tab. `fragment` merges `config/a17.fragment` (PSI, memcg, BPF) for Android 17.
- `scripts/repack_boot.py STOCK_boot.img Image OUT_boot.img` swaps the kernel in the stock boot image (header v1, no ramdisk, AVB footer kept; flash vbmeta disabled). Flashing is a separate gate: Download mode, user OK, stock boot image kept.
