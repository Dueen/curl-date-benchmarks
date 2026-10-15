# Native x86 curl date benchmark results

Both packed candidates were run successfully on three free standard GitHub Actions x86-64 VMs using GCC 14.2.0 and Clang 17.0.6 at O2/O3. All tests and differential checks passed. No upstream curl PR was opened.

**Conclusion:** x86 substantially improves the case for packed lookups, especially weekdays, but neither implementation is a universal complete-parser improvement. Results vary by CPU, compiler and workload, and regressions remain. The two-byte version is not consistently better than the three-byte version.

- Repository: https://github.com/Dueen/curl-date-benchmarks
- Successful run: https://github.com/Dueen/curl-date-benchmarks/actions/runs/38770615347
- Benchmark commit: `611de4479a33a1d6b44df1ec3cab97d3a907f933`
- curl baseline: `653f7d7fa983938c4c9331d14c71bc9fa5a5aba8`

## Hosts and scope

| Replicate | Native x86 CPU | Job |
|---|---|---|
| 1 | INTEL(R) XEON(R) PLATINUM 8573C | https://github.com/Dueen/curl-date-benchmarks/actions/runs/38770615347/job/116545163478 |
| 2 | AMD EPYC 7763 64-Core Processor | https://github.com/Dueen/curl-date-benchmarks/actions/runs/38770615347/job/116545164598 |
| 3 | AMD EPYC 9V74 80-Core Processor | https://github.com/Dueen/curl-date-benchmarks/actions/runs/38770615347/job/116545163803 |

These runs match the original report’s x86-64 architecture and compiler versions, not its unidentified CPU or older standalone harness. All candidates here use the pinned current-master baseline and complete parser. The ARM64 experiment used different compiler versions; its contrast with x86 should not be attributed solely to architecture. Within this x86 run, the same GCC/Clang versions ran across Intel and AMD CPUs.

## Original complete-parser benchmark

Percentages are median paired changes in latency; **negative means faster**. Ranges below are the minimum and maximum of the three per-VM medians, not confidence intervals or pooled results.

| Compiler | Three-byte: range across 3 VMs | Two-byte: range across 3 VMs |
|---|---:|---:|
| clang-O2 | -11.06% to -4.16% | -12.86% to -10.82% |
| clang-O3 | -8.87% to -1.41% | -7.76% to +7.78% |
| gcc-O2 | -4.11% to -0.32% | -2.73% to +1.32% |
| gcc-O3 | -3.23% to +17.83% | -4.15% to +17.90% |

| CPU | Candidate | Clang O2 | Clang O3 | GCC O2 | GCC O3 |
|---|---|---:|---:|---:|---:|
| INTEL(R) XEON(R) PLATINUM 8573C | pack3 | -4.16% | -1.41% | -0.32% | +17.83% |
| INTEL(R) XEON(R) PLATINUM 8573C | pack2 | -12.02% | +7.78% | +1.32% | +17.90% |
| AMD EPYC 7763 64-Core Processor | pack3 | -11.06% | -6.58% | -4.06% | -3.23% |
| AMD EPYC 7763 64-Core Processor | pack2 | -10.82% | -7.76% | -2.73% | -4.15% |
| AMD EPYC 9V74 80-Core Processor | pack3 | -9.90% | -8.87% | -4.11% | +3.75% |
| AMD EPYC 9V74 80-Core Processor | pack2 | -12.86% | -0.17% | -1.27% | +3.29% |

The original curl benchmark parses its unmodified 183-date corpus in source order: 20,000 loops per sample, 15 paired baseline/candidate samples per configuration, randomized binary order. Each sample performs 3,660,000 parser calls; all samples preserve exactly 1,120,000 rejected dates in both sources. Those rejections are deliberate malformed/unsupported corpus entries, not test failures.

GCC O3 is a material counterexample to a blanket speed claim: both packings regress about 18% on the Intel Xeon, improve 3–4% on EPYC 7763, and regress 3–4% on EPYC 9V74. Three-byte Clang improves the original corpus on all three hosts; two-byte Clang O3 ranges from faster to slower. A single average would hide these differences.

## Randomized complete-parser corpus

| CPU | Candidate | Clang O2 | Clang O3 | GCC O2 | GCC O3 |
|---|---|---:|---:|---:|---:|
| INTEL(R) XEON(R) PLATINUM 8573C | pack3 | -3.94% | -5.63% | -7.21% | +4.24% |
| INTEL(R) XEON(R) PLATINUM 8573C | pack2 | -2.47% | -2.05% | -0.86% | +3.94% |
| AMD EPYC 7763 64-Core Processor | pack3 | +4.55% | +3.24% | -3.09% | -3.89% |
| AMD EPYC 7763 64-Core Processor | pack2 | +3.36% | -9.95% | -0.19% | -8.85% |
| AMD EPYC 9V74 80-Core Processor | pack3 | -7.32% | -11.05% | -7.20% | -6.61% |
| AMD EPYC 9V74 80-Core Processor | pack2 | -7.69% | -6.55% | -4.44% | -5.99% |

This workload uses a reproducible random 1,024-entry sample from the same corpus, including valid and invalid entries, repeated 256 times per sample for 21 paired rounds. It shuffles workload order and implementation order. Differences from the original corpus illustrate sensitivity to token mix and repetition/order. Other recorded workloads cover valid-only/invalid-only corpus subsets, generated RFC1123/RFC850/asctime dates and a numeric control.

## Isolated lookups

| CPU | Candidate | Workload | Clang O2 | Clang O3 | GCC O2 | GCC O3 |
|---|---|---|---:|---:|---:|---:|
| INTEL(R) XEON(R) PLATINUM 8573C | pack3 | month-valid | -62.82% | -62.35% | -62.78% | -62.78% |
| INTEL(R) XEON(R) PLATINUM 8573C | pack3 | day-valid | -59.31% | -61.00% | -41.89% | -45.63% |
| INTEL(R) XEON(R) PLATINUM 8573C | pack3 | day-invalid-ascii | +9.39% | -11.52% | +6.72% | +64.41% |
| INTEL(R) XEON(R) PLATINUM 8573C | pack3 | month-nearmiss | +17.00% | +43.45% | +52.84% | +31.20% |
| INTEL(R) XEON(R) PLATINUM 8573C | pack2 | month-valid | -52.50% | -54.70% | -65.78% | -63.26% |
| INTEL(R) XEON(R) PLATINUM 8573C | pack2 | day-valid | -59.06% | -60.07% | -39.81% | -44.55% |
| INTEL(R) XEON(R) PLATINUM 8573C | pack2 | day-invalid-ascii | +10.49% | -8.18% | +2.25% | +5.57% |
| INTEL(R) XEON(R) PLATINUM 8573C | pack2 | month-nearmiss | +35.55% | +34.29% | +34.15% | +39.08% |
| AMD EPYC 7763 64-Core Processor | pack3 | month-valid | -55.05% | -44.09% | -35.91% | -42.54% |
| AMD EPYC 7763 64-Core Processor | pack3 | day-valid | -56.13% | -54.22% | -49.83% | -52.05% |
| AMD EPYC 7763 64-Core Processor | pack3 | day-invalid-ascii | +2.91% | +7.01% | +12.49% | +11.43% |
| AMD EPYC 7763 64-Core Processor | pack3 | month-nearmiss | -3.84% | +8.75% | +71.10% | +9.71% |
| AMD EPYC 7763 64-Core Processor | pack2 | month-valid | -39.81% | -46.91% | -42.59% | -46.53% |
| AMD EPYC 7763 64-Core Processor | pack2 | day-valid | -53.28% | -54.80% | -53.27% | -49.88% |
| AMD EPYC 7763 64-Core Processor | pack2 | day-invalid-ascii | +4.63% | -3.63% | +6.91% | -1.00% |
| AMD EPYC 7763 64-Core Processor | pack2 | month-nearmiss | +36.08% | +26.20% | +57.53% | +25.04% |
| AMD EPYC 9V74 80-Core Processor | pack3 | month-valid | -21.03% | -11.34% | +4.99% | -20.68% |
| AMD EPYC 9V74 80-Core Processor | pack3 | day-valid | -43.97% | -43.01% | -37.42% | -32.25% |
| AMD EPYC 9V74 80-Core Processor | pack3 | day-invalid-ascii | -2.49% | -5.15% | -17.52% | -9.63% |
| AMD EPYC 9V74 80-Core Processor | pack3 | month-nearmiss | -6.98% | +23.27% | +35.66% | +31.24% |
| AMD EPYC 9V74 80-Core Processor | pack2 | month-valid | +0.49% | -15.54% | -21.80% | -8.98% |
| AMD EPYC 9V74 80-Core Processor | pack2 | day-valid | -45.22% | -46.27% | -32.37% | -28.74% |
| AMD EPYC 9V74 80-Core Processor | pack2 | day-invalid-ascii | -3.21% | -14.17% | -15.77% | +1.94% |
| AMD EPYC 9V74 80-Core Processor | pack2 | month-nearmiss | +31.37% | +9.36% | +12.44% | +20.16% |

Valid weekday lookup has 29–61% lower latency across both packings and all measured x86 configurations. Valid-month gains vary considerably; the three-byte GCC O2 month lookup is about5% slower on EPYC 9V74. Invalid-input regressions remain, including month near misses and some invalid weekday cases. Correct-suffix/wrong-first-character inputs often improve strongly. Other counterexamples include a 45.40% short-weekday regression (Intel, two-byte Clang O2; 1.35 to 1.97 ns/call) and a 6.49% generated RFC1123 regression (EPYC 7763, three-byte Clang O2), despite that configuration improving the original ordered corpus. Full 18-workload results, ns/call medians and descriptive bootstrap intervals are in [combined summary CSV](recorded-results/x86-2026-10-15.csv) and the per-job bundles. No isolated lookup percentage is presented as a curl-wide speedup.

## Verification and reproducibility

- All three jobs completed successfully. For each VM, baseline, pack2 and pack3 each passed all 75 runnable unit tests and all 21 selected date-related HTTP/FTP/unit cases. These selections overlap; do not sum them as unique tests. Platform/feature skips remain in the logs. TLS/HSTS is outside the configured test build.
- Every compiler/optimization comparison passed exhaustive differential checks on all 16,777,216 byte triplets, including NUL/high-bit values and an exactly 3-byte allocation; short allocations, full weekday case/prefix combinations, the 183-date corpus and 100,000 random ASCII parser inputs also passed.
- Both candidates passed Clang 17 ASan/UBSan in default and forced-unsigned-char builds. Signed and unsigned run evidence is preserved separately. Every compiler/optimization configuration also compiled the parse-disabled translation units; this workflow does not claim full Linux parse-disabled builds. Full disabled builds were tested separately on ARM64.
- Every extracted bundle passed compressed-bundle SHA256 validation and its complete per-file manifest. Baseline and candidate source snapshots exactly match the locally reviewed files.
- Timed parser objects and parsing/string dependencies are compiled independently at the stated optimization, without DEBUGBUILD or LTO. Separate UNITTESTS objects expose lookup functions; complete-parser objects retain normal static visibility/inlining. The Debug CMake archive supplies formatting/timing helpers outside the parser-call hot path.
- All builds and functional tests finish before timing. Timed executables are pinned to one allowed logical CPU. Pair execution order is randomized. Candidate-order shuffling happened to produce pack3 then pack2 in all three seeds; therefore these are paired comparisons against baseline, not randomized direct pack2-versus-pack3 comparisons.
- The VMs are shared infrastructure. CPU affinity does not lock frequency or isolate physical cores, and no hardware performance counters or executable-alignment controls were used. The numeric-only control changes by roughly-4% to+11% depending on configuration; inlining/code layout and VM variability are possible contributors, not established causes.
- Do not pool per-round bootstrap intervals across different CPUs as though all samples came from one machine. The report preserves each host separately.

## Assembly and interpretation

Compiler assembly, ELF disassembly, text sizes and static instruction/branch counts are included in every job bundle. Those are static sites rather than dynamic execution counts. GCC O3 normal parsedate text is 3,739 bytes for baseline, 3,563 for pack2 and 3,227 for pack3 on all three hosts; smaller code still coexists with the Intel ordered-corpus regression.

These native results support further targeted investigation, rather than rejecting packing based only on ARM64. They also prevent claiming a universally faster replacement. The three-byte candidate has the more consistent Clang ordered-corpus result here, while two-byte wins selected lookup configurations; neither dominates all compiler/CPU/input combinations. No upstream PR was opened and the original curl working-tree changes were preserved.

## Free execution path

Only standard ubuntu-24.04 public-repository runners were used. The workflow is manual-only, has a public-repository guard and uses no caches, paid artifact uploads, larger runners or cloud resources. Evidence was encoded in job logs and decoded locally. GitHub documents public standard-runner compute as free and excludes job logs/summaries from artifact-storage usage: https://docs.github.com/en/billing/concepts/product-billing/github-actions . No paid benchmark service was used.

Raw job logs, verified bundles, source snapshots, scripts, exact commands, CPU metadata, timings and assembly are retained in the downloadable local evidence package. The public benchmark repository and successful run provide an independent audit trail.
