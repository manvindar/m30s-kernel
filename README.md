# Kernel for the Samsung Galaxy M30s (SM-M307F)

Builds Samsung's official open-source kernel (Linux 4.14.113, `exynos9610-m30sdd_defconfig`, Android 11 drop `SM-M307F_SWA_RR`) on GitHub Actions. Mac is too small for it.

- `Kernel.tar.gz` (181 MB, over git's file limit) is a release asset named `source-SM-M307F_SWA_RR`; the workflow downloads it. Private repo: Samsung's GPL source, keep it private unless decided otherwise.
- Toolchains are Samsung's: AOSP `clang-4639204` and gcc 4.9 from tag `android-9.0.0_r30`.
- Run `Build kernel` from the Actions tab. `fragment` merges `config/a17.fragment` (PSI, memcg, BPF) for Android 17.
- `scripts/repack_boot.py STOCK_boot.img Image OUT_boot.img` swaps the kernel in the stock boot image (header v1, no ramdisk, AVB footer kept; flash vbmeta disabled). Flashing is a separate gate: Download mode, user OK, stock boot image kept.

## Versions (releases)
- `kernel-4.14.113-a17` (Latest): stock config + PSI (28 Android common patches), BPF JIT, userfaultfd. The baseline the port repo pulls.
- `kernel-4.14.113-a17-perf` (prerelease): + `-O2`, lz4 in the crypto API (set zram `comp_algorithm=lz4` at runtime), BBR + fq, BFQ (needs blk-mq: `CONFIG_SCSI_MQ_DEFAULT` stays off), debug options off.
- `kernel-4.14.113-a17-boost` (prerelease): perf + a touch boost driver (`boost/input_boost_m30s.c`): CPU min frequency on both clusters for 150 ms after touch; tune in `/sys/module/input_boost_m30s/parameters/`.
- CPU/GPU clocks are not raised: the OPP tables come from the ECT/ACPM firmware and the device tree (`dtb` partition), not from this source. The top steps are 2.314 GHz (A73) and 1.742 GHz (A53).
- Experimental builds are prereleases; promote a blessed one with `gh release edit TAG --latest`.
