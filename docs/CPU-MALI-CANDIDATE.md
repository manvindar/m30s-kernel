# CPU/Mali kernel candidate

Experimental SM-M307F kernel built on the v0.6 Pixel performance profile. This is a separate candidate, not a replacement for the verified v0.6 release. No fresh device flash or runtime acceptance has been performed.

- CPU: invalidate schedutil's raw-frequency cache when an up/down rate limit rejects a request and when shared deadline paths bypass that cache. The actual extracted C functions reproduce the stuck-frequency behavior before the patch and pass upward/downward expiry cases afterward. Deadline branches were source-reviewed, not exercised by the host harness.
- GPU: add `WQ_HIGHPRI` to three existing Mali R26 maintenance workqueues: cache cleaning, reset, and MMU page-fault handling. This is experimental scheduling policy; it can compete with other priority work. Rendering speed, stability, temperature and battery effects are unmeasured.

Only four kernel files change. The existing PSI series and checked performance configuration remain intact. No AIGo code, newer Mali driver, CPU/GPU maximum clocks, thermal changes, HDR, storage queue changes, force-load bypass or security-policy changes are included.

The version label remains `4.14.113-perf-20261110`; use the distinct release tag, source commit and image checksums to identify this candidate. New builds use `Manvindar Singh@github-actions` in the compiled banner. LZ4 remains a capability; the ROM uses zstd zram.

Assets include the raw ARM64 `Image`, a repacked `boot-a17-perf.img`, exact configuration, checksums and source/build/boot receipts. These are not a flashable ZIP. Keep the existing v0.6 boot image and matching Samsung firmware for rollback. Build authorization alone does not authorize another device flash.

## Provenance

Donor: [sundrams-playground/kernel_samsung_exynos9610](https://github.com/sundrams-playground/kernel_samsung_exynos9610), pinned `7e53227ad44b83be937c6a03941815ed0bd13c0a`.

CPU subset: [735229a1f628cbbfc886072a7716b4be797def3e](https://github.com/sundrams-playground/kernel_samsung_exynos9610/commit/735229a1f628cbbfc886072a7716b4be797def3e), original author John Dias. The donor's separate AIGo edit is excluded because this baseline lacks that file.

Mali flags: [6bce9047d99abac37be688b7575e3150c5a2bf55](https://github.com/sundrams-playground/kernel_samsung_exynos9610/commit/6bce9047d99abac37be688b7575e3150c5a2bf55), original author repinger. Patch headers retain upstream metadata and sign-offs.

The build rejects drift in each patch and in every touched baseline/source output. Source application and host regressions do not prove native or hardware behavior; native compilation and subsequent device tests are separate gates.
