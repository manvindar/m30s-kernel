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
