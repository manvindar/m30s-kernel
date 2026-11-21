# Galaxy M30s SM-M307F kernel

Public build and patch source for Samsung Linux 4.14.113 (`exynos9610-m30sdd_defconfig`, Android 11 source drop `SM-M307F_SWA_RR`). Upstream Samsung source is provided as `Kernel.tar.gz` in the [source release](https://github.com/manvindar/m30s-kernel/releases/tag/source-SM-M307F_SWA_RR), because it exceeds GitHub's Git file-size limit.

[Kernel releases](https://github.com/manvindar/m30s-kernel/releases) include raw ARM64 Image, exact kernel.config, repack tool and checksums. The Pixel ROM uses **kernel-4.14.113-a17**. Performance/boost variants are experimental; HDR variants caused black video on this SDR panel and should not be used for the Pixel ROM.

The Build kernel workflow uses Samsung's AOSP clang-4639204 and GCC4.9 toolchains from `android-9.0.0_r30`. Enable `fragment` to apply the PSI patch series and merge `config/a17.fragment` for Android 17. Full build commands and compatibility steps are in [.github/workflows/build-kernel.yml](.github/workflows/build-kernel.yml).

For a dated version label on the existing Pixel baseline, set `version_date=20261110`, `fragment=true`, and leave `perf`, `boost`, and `hdr` false. This produces release string `4.14.113-perf-20261110` and a matching boot image. It uses the hash-pinned archived baseline source and exact release configuration. Only `CONFIG_LOCALVERSION` and automatic SCM labeling change; the build rejects any functional configuration difference. The `-perf` suffix is the requested label and does not enable `config/perf.fragment`. Kernel module CRC validation remains enabled, with forced loading disabled. About phone reads the resulting actual kernel release and build date. Runtime/module acceptance remains pending device verification.

This baseline uses permissive SELinux. Kernel builds alone do not prove hardware compatibility. Flashing requires the correct model, an unlocked bootloader, off-device backups and matching stock firmware for rollback. Read the Pixel port's [flashing guide](https://github.com/manvindar/m30s-pixel-port/blob/main/docs/FLASH.md).

Git author metadata was sanitized before publication. The original history, build logs and releases remain in a private archive. Existing private checkouts must not push old history here; use a fresh clone of this public repository. Upstream patch authors and license information are preserved.

### Pixel performance profile

`performance_profile=true`, `version_date=20261110`, `fragment=true` builds the authenticated Android 17 baseline with a separate, checked performance allowlist. Leave legacy `perf`, `boost`, and `hdr` inputs false. The actual release string remains `4.14.113-perf-20261110`; use a distinct release tag for the functional profile.

This profile enables compiler `-O2`, LZ4 compression support, BBR with Fair Queue as the network defaults, and the existing 150 ms touch boost through Samsung CPU minimum-frequency requests. Maximum clocks and thermal controls stay unchanged. Atomic-sleep and power-management debug instrumentation are disabled. Touch event throttling is synchronized and failed handler registration releases its frequency requests. The final generated configuration must match the allowlist exactly, including dependencies; module CRC validation remains enabled.

LZ4 is available but the ROM's existing zstd zram setting stays in place. Network defaults can be overridden by Android at runtime. Speed, battery, networking and module compatibility require device checks; these are performance candidates, not measured improvements. BFQ and Samsung's storage queue mode stay unchanged because enabling BFQ alone does not activate it on the existing UFS path. HDR, GPU/MIF clock locks, resolution changes, security changes and uncompiled donor backports are excluded.

Future builds use `KBUILD_BUILD_USER="Manvindar Singh"` and `KBUILD_BUILD_HOST=github-actions`, so the compiled Linux banner identifies the owner as `Manvindar Singh@github-actions`. Existing release images keep their original banner and checksums.

### Narrow CPU/Mali candidate

Enable `cpu_mali=true` together with `performance_profile=true`, `fragment=true`, `version_date=20261110` and legacy perf/boost/hdr=false. Use a distinct prerelease tag. See [candidate scope and test limits](docs/CPU-MALI-CANDIDATE.md). The v0.6 device-verified kernel remains the rollback baseline.

### Mint-port extras (`extras` input, branch `feat/mint-port`)

Features taken from the [Mint kernel](https://github.com/SamsungM30s/kernel_samsung_m307f/tree/mint) (4.14.223, same Exynos 9610 family) and applied on this 4.14.113 source. Kernel version stays 4.14.113 (no stable bump). **Builds only: every item below compiled and linked in GitHub Actions; nothing has been run on a device.** Default builds are untouched: with `extras` empty no new step runs, and a dated-baseline build from this branch (run 44873113465) has the same Image sha256 as one from `main` (run 44873705665, `a030ac17...`).

Usage: `fragment=true extras=memfd,pidfd,wireguard,deknox,kernelsu` (or `extras=all`, which means those five). `extras=lto` is separate and is not part of `all`. Extras require `fragment=true` and refuse `version_date`, `performance_profile` and `cpu_mali`, so the checked baseline and reviewed profiles are never mixed with them. The release string becomes `4.14.113-a17-mint`. Each extra needs its own patches (`patches/extras/<name>`, upstream authorship and Signed-off-by kept) and config (`config/extras-<name>.fragment`); a dropped or overridden extras symbol fails the build, and the workflow checks the feature symbols are in `System.map`.

| extra | what | source | config | CI |
|---|---|---|---|---|
| `memfd` | memfd `F_SEAL_FUTURE_WRITE` (2 patches) | Mint `36578719fff4` (android-4.14 backport) + upstream `05d351102dbe` (private-mapping COW fix). Upstream `22247efd822e` (hugetlb) is not needed: this tree has no hugetlb file sealing | `CONFIG_SHMEM=y` | green, run 44816740634 |
| `pidfd` | `pidfd_send_signal`, `CLONE_PIDFD`, pidfd poll, `pidfd_open` (434), `P_PIDFD` for waitid (15 patches) | Mint android-4.14 backports (14 commits, Christian Brauner, Joel Fernandes, Suren Baghdasaryan and others) + one own patch adding `pidfd_send_signal` (424) to the arm64 compat table, which the backport omitted | none (anon_inodes made unconditional) | green, same run |
| `wireguard` | in-tree wireguard-linux-compat (5 patches) | Mint `b5ce6a69aeac`, `e4ea70307dd2`, `0473adfa0b08`, `bb8c2bd51ec7` (wg-1.0.20210606), `f22a34b0c803` (sync, 2022) | `CONFIG_WIREGUARD=y`, debug off | green, same run |
| `deknox` | Samsung hardening off, config only | Mint `exynos9610-m30s_core_defconfig` and `kernel/configs/mint_partial-deknox-*.config` | see below | green, same run |
| `kernelsu` | KernelSU v0.9.2 with manual hooks (2 patches) | Mint `6c81f9861b2c` (hooks in exec, open, read_write, stat, input, selinux `check_nnp_nosuid`) and `e13c09a07cc1` (drivers Kconfig/Makefile). KernelSU is cloned at pinned commit `3291538446b7fccec46fa52775e6bf594c77b9f4` (tag v0.9.2, as Mint) | `CONFIG_KSU=y`, `CONFIG_OVERLAY_FS=y` (a KernelSU dependency, off in stock); `CONFIG_KPROBES` stays off | green, same run |
| `lto` | clang full LTO (`CONFIG_LTO_CLANG=y`) | tree already carries android-4.14 `LTO_CLANG`; Mint `9edb942a918d` + `38548d76e0de` (stpcpy) and own tzdev patch (`tz_deploy_tzar.o` built without LTO) | `CONFIG_LTO_CLANG=y`, CFI off | green, run 44872042278 |

All-but-LTO run 44816740634: Image sha256 `3b7e314bb16277fbd9be36b02a71632a2819d42458e78df8028f20b7ba74cc8d` (artifact `kernel`, with `extras-receipt.txt`). LTO run 44872042278: Image sha256 `c2dac663c1aee0d492818b194274826e7edd87f95ff4754846b9a19a4ca67ca3`. These were built from separate runs; the LTO image has none of the other extras (only PSI/a17 fragment plus LTO). `CONFIG_USERFAULTFD=y` was already in `config/a17.fragment`; the `sys_userfaultfd` symbol is linked in both images.

**What `deknox` turns off.** Already off in the stock m30sdd defconfig and re-asserted: `UH`, `UH_LKMAUTH`, `UH_LKM_BLOCK` (Samsung uH/RKP hypervisor; `RKP`, `KDP` symbols do not exist in this source), `FIVE`, `PROCA`, `SECURITY_DEFEX`, `SEC_RESTRICT_ROOTING`. Turned off here, on in stock: `SECURITY_DSMS` and `INTEGRITY`. Kept on, as Mint keeps them: `SDP`, `FSCRYPT_SDP`, `DDAR`, `KNOX_NCM`, `DM_VERITY`, `TZDEV`. Mint's `5c448137d01c` (fscrypt Knox-flag compatibility) is not ported. This is not a security improvement; it removes Samsung checks and the device keeps its permissive-SELinux baseline.

**LTO toolchain.** The old clang-4639204 cannot do kernel LTO, so only `extras=lto` uses proton-clang 13.0.0 (`kdrag0n/proton-clang` commit `9fb011b183fe7e69b04b873ef6533b4b077e3c5e`, `https://github.com/kdrag0n/proton-clang/archive/9fb011b183fe7e69b04b873ef6533b4b077e3c5e.tar.gz`, sha256 `7358f655bd5af997990f208212da2687a9cd4d53cb4f1811d6035487e04076b8`, verified before use). It links with proton's gold and `LLVMgold.so`, with `-Wno-error` since clang 13 warns far more than clang 6. Boot, stability and performance of an LTO kernel are unknown.

**Tuned scheduler (EMS revamp): not ported.** Mint's EMS rework (`2b7c68d955ca`, Jul 2022, and about 130 follow-ups by John Vincent) sits on top of a uclamp backport, cgroup/cpuset, fair/rt/core and PSI rework: against the A505F base the sched paths change by about 18k lines. Applied in order onto this tree, 57 of 198 candidate commits reject (236 failed hunks), and the rest cannot be judged without the rejected ones. A commit inventory is in [docs/MINT-EMS-COMMITS.txt](docs/MINT-EMS-COMMITS.txt). Doing it properly means porting the uclamp chain first and testing on hardware.
