# Work-reduction experiment results

Two independent candidates were benchmarked against curl `653f7d7fa983938c4c9331d14c71bc9fa5a5aba8`: constant full-weekday suffix lengths and a three-line exact-uppercase GMT/UTC fast path before the existing timezone binary search. Neither is combined with the previous packed month/weekday variants. No upstream PR was opened.

**Decision:** the timezone fast path is the strongest candidate for a focused upstream review. Constant weekday lengths do not establish a consistent complete-parser gain. The timezone change has measured fallback-path regressions and increases code size; this is not a universal speedup or a curl-wide throughput claim.

## Runs and hosts

Both manual runs used benchmark commit `e5ffd52484741bfce09b9badf52f754c9e8d1505`, standard public Ubuntu 24.04 x86-64 VMs, GCC 14.2.0 and Clang 17.0.6 at O2/O3. Six VMs provide 24 compiler/VM configurations per candidate. Runs A and B repeat the same source and random seeds on independently allocated VMs.

| VM | CPU | Successful run |
|---|---|---|
| A1 | AMD EPYC 7763 64-Core Processor | [job](https://github.com/Dueen/curl-date-benchmarks/actions/runs/38774868730/job/116559795083) |
| A2 | AMD EPYC 9V74 80-Core Processor | [job](https://github.com/Dueen/curl-date-benchmarks/actions/runs/38774868730/job/116559794686) |
| A3 | AMD EPYC 7763 64-Core Processor | [job](https://github.com/Dueen/curl-date-benchmarks/actions/runs/38774868730/job/116559794323) |
| B1 | AMD EPYC 9V45 96-Core Processor | [job](https://github.com/Dueen/curl-date-benchmarks/actions/runs/38775638868/job/116562437921) |
| B2 | AMD EPYC 9V74 80-Core Processor | [job](https://github.com/Dueen/curl-date-benchmarks/actions/runs/38775638868/job/116562438304) |
| B3 | AMD EPYC 9V45 96-Core Processor | [job](https://github.com/Dueen/curl-date-benchmarks/actions/runs/38775638868/job/116562438044) |

All six VMs landed on AMD EPYC processors (three CPU models). These batches did not test Intel; the earlier packed-lookup run included Intel, but that is not evidence for this different timezone patch.

## Original complete-parser benchmark

Latency changes use the median of paired candidate/baseline ratios; negative means faster. Each configuration has 15 shuffled-order pairs, with 20,000 passes over the unmodified 183-date curl corpus per sample (3,660,000 parser calls). Every sample preserves the same 1,120,000 rejected dates. These rejected corpus entries are intentional, not test failures.

| Candidate | Range of 24 per-VM/compiler medians | Descriptive interval: faster / slower / overlaps zero |
|---|---:|---:|
| weekday_lengths | -0.91% to +1.57% | 2 / 5 / 17 |
| tz_fastpath | -4.97% to -0.54% | 21 / 0 / 3 |

| VM | Compiler | Weekday lengths | GMT/UTC fast path | Fast-path bootstrap interval |
|---|---|---:|---:|---:|
| A1 | clang-O2 | -0.77% | -3.16% | -3.65% to -2.84% |
| A1 | clang-O3 | +1.57% | -2.04% | -7.22% to -1.38% |
| A1 | gcc-O2 | +0.17% | -2.50% | -2.60% to -2.12% |
| A1 | gcc-O3 | -0.19% | -4.28% | -4.83% to -3.65% |
| A2 | clang-O2 | +0.60% | -4.97% | -5.25% to -3.99% |
| A2 | clang-O3 | -0.64% | -1.20% | -3.14% to +0.00% |
| A2 | gcc-O2 | +0.50% | -1.49% | -1.84% to -1.35% |
| A2 | gcc-O3 | +0.14% | -3.47% | -3.67% to -3.24% |
| A3 | clang-O2 | -0.91% | -2.90% | -3.42% to -2.09% |
| A3 | clang-O3 | +0.89% | -1.96% | -2.39% to -0.94% |
| A3 | gcc-O2 | +0.11% | -2.38% | -2.83% to -1.62% |
| A3 | gcc-O3 | -0.02% | -4.11% | -4.74% to -3.55% |
| B1 | clang-O2 | -0.16% | -2.14% | -2.58% to -1.64% |
| B1 | clang-O3 | +0.36% | -2.00% | -2.60% to -0.16% |
| B1 | gcc-O2 | +0.44% | -1.79% | -2.59% to -1.54% |
| B1 | gcc-O3 | -0.04% | -3.06% | -3.68% to -2.75% |
| B2 | clang-O2 | +0.65% | -4.62% | -5.02% to -3.96% |
| B2 | clang-O3 | -0.60% | -2.96% | -3.64% to -2.43% |
| B2 | gcc-O2 | +0.11% | -1.33% | -1.95% to -0.51% |
| B2 | gcc-O3 | +0.24% | -3.48% | -3.67% to -2.59% |
| B3 | clang-O2 | +0.04% | -0.54% | -2.01% to +0.23% |
| B3 | clang-O3 | -0.35% | -1.82% | -3.33% to -0.63% |
| B3 | gcc-O2 | +1.53% | -1.55% | -2.87% to +0.60% |
| B3 | gcc-O3 | -0.40% | -3.17% | -3.73% to -2.99% |

## Targeted gains and regressions

Ranges below are minima/maxima of the 24 per-configuration paired medians, not confidence intervals or pooled samples. Each workload has 21 paired rounds using reproducible 1,024-entry datasets repeated 256 times. Workload and implementation order are shuffled.

| Candidate | Workload | Latency range | Interval: faster / slower / overlaps zero |
|---|---|---:|---:|
| weekday_lengths | day-full | -22.50% to +1.68% | 20 / 2 / 2 |
| weekday_lengths | parser-rfc850 | -8.99% to +1.36% | 16 / 2 / 6 |
| weekday_lengths | parser-corpus-random | -9.84% to +4.91% | 14 / 5 / 5 |
| weekday_lengths | parser-numeric | -2.98% to +3.29% | 9 / 4 / 11 |
| tz_fastpath | tz-gmt | -54.81% to -31.22% | 24 / 0 / 0 |
| tz_fastpath | tz-utc | -53.83% to -20.04% | 24 / 0 / 0 |
| tz_fastpath | tz-other-three | -8.32% to +18.00% | 5 / 8 / 11 |
| tz_fastpath | tz-four | -9.31% to +3.03% | 7 / 1 / 16 |
| tz_fastpath | tz-invalid-three | -12.93% to +19.16% | 6 / 14 / 4 |
| tz_fastpath | tz-invalid-four | -15.00% to +9.64% | 5 / 3 / 16 |
| tz_fastpath | tz-short | -12.68% to +4.39% | 6 / 2 / 16 |
| tz_fastpath | parser-gmt | -7.06% to -1.89% | 24 / 0 / 0 |
| tz_fastpath | parser-utc | -7.00% to -0.79% | 24 / 0 / 0 |
| tz_fastpath | parser-other-three-zone | -3.76% to +1.80% | 10 / 4 / 10 |
| tz_fastpath | parser-four-zone | -4.14% to +2.44% | 12 / 7 / 5 |
| tz_fastpath | parser-invalid-zone | -4.86% to +2.17% | 10 / 5 / 9 |
| tz_fastpath | parser-corpus-random | -8.15% to -0.69% | 22 / 0 / 2 |
| tz_fastpath | parser-numeric | -4.36% to +1.50% | 7 / 6 / 11 |

The GMT/UTC path bypasses binary search for exact common keys. Other three-character keys that reach this branch still traverse the existing search after paying for the new comparisons. Report both these lookup costs and full-parser fallback cases; isolated lookup percentages do not establish application throughput gains. Unchanged lookup/control workloads also show variation, so small deltas cannot be attributed solely to the source change.

## Generated code

Counts below are static emitted instruction/branch sites, not dynamically executed instructions or hardware counters. Normal parser-object text sizes include alignment and all emitted functions. The assembly metrics match across the six VMs for a given compiler configuration.

| Candidate | Compiler | Normal .text bytes (base → candidate) | Conditional branches (base → candidate) | Target lookup instructions (base → candidate) |
|---|---|---:|---:|---:|
| weekday_lengths | clang-O2 | 2834 → 2866 | 119 → 119 | 131 → 121 |
| weekday_lengths | clang-O3 | 3170 → 3202 | 143 → 143 | 131 → 121 |
| weekday_lengths | gcc-O2 | 3339 → 3291 | 141 → 141 | 126 → 112 |
| weekday_lengths | gcc-O3 | 3739 → 3739 | 154 → 154 | 121 → 121 |
| tz_fastpath | clang-O2 | 2834 → 2914 | 119 → 121 | 88 → 99 |
| tz_fastpath | clang-O3 | 3170 → 3186 | 143 → 145 | 93 → 101 |
| tz_fastpath | gcc-O2 | 3339 → 3355 | 141 → 143 | 103 → 114 |
| tz_fastpath | gcc-O3 | 3739 → 3787 | 154 → 156 | 103 → 114 |

GCC O3 already eliminates the weekday suffix strlen call in the baseline; its weekday lookup instruction count and normal parser-object text size do not improve. The timezone fast path adds two conditional branch sites to the normal parser object and 16–80 text bytes depending on compiler/optimization. Its common path can execute less work despite a larger static instruction count.

## Local ARM64 follow-up

On the local macOS ARM64 host, Apple Clang 21.0.0 and Homebrew GCC 16.2.0 ran the same original parser benchmark with 15 shuffled-order pairs per configuration. This is a separate compiler/platform comparison; it does not isolate the effect of architecture. macOS timings were not CPU-pinned. These are complete-parser measurements, without the 30-workload timing matrix.

| Compiler | Weekday lengths | GMT/UTC fast path | Fast-path bootstrap interval |
|---|---:|---:|---:|
| clang-O2 | -0.04% | -6.42% | -6.89% to -6.02% |
| clang-O3 | -0.26% | -5.91% | -6.27% to -5.86% |
| gcc-O2 | +0.35% | -8.27% | -8.49% to -7.53% |
| gcc-O3 | +0.00% | -4.89% | -5.24% to -3.83% |

## Correctness and reproducibility

- On each of six x86 VMs, baseline and both candidates each passed all 75 runnable unit tests and 21 selected date-related tests, including unit4781 and HTTP/FTP date handling. Selections overlap; they are not 96 unique tests. TLS/HSTS is outside this TLS-disabled configuration.
- Both candidates passed Clang ASan/UBSan in default and forced unsigned-char modes on all six VMs (24 sanitizer runs). Checks compare all 256^3 byte triples for weekday/month lookup, all 128^3 ASCII timezone triples, all 26^4 uppercase four-letter zones, exact-size/short allocations, weekday cases/lengths, 183 corpus dates, 100,000 random ASCII parser inputs and all 30 datasets. Every GCC/Clang O2/O3 build also passed these comparisons and compiled parse-disabled translation units.
- The local ARM follow-up passed all four compiler/optimization differential checks for both candidates, plus the earlier local ASan/UBSan checks. It did not rerun the full curl unit/integration selection for these candidates locally; those selections ran on x86.
- Every extracted log bundle passed compressed SHA256 and per-file manifest validation. Recorded baseline/candidate snapshots match the committed source files. Both candidate patches apply cleanly to the pinned baseline and pass curl checksrc.
- All x86 builds and functional tests finish before timing; timed executables are pinned to one allowed logical CPU. Candidate order alternates by replicate parity (2:1 per three-VM batch); pairs are randomized. Neither frequency nor physical-core isolation is controlled on hosted VMs.
- Bootstrap intervals describe within-VM paired samples. They do not capture all VM/frequency/code-layout variability, are not adjusted for multiple comparisons, and must not be pooled across CPUs. The second run repeats rather than introducing new random seeds.
- Timed parser/string dependencies are independently optimized without DEBUGBUILD or LTO. UNITTESTS objects expose isolated lookups; complete parser objects retain ordinary static visibility/inlining. The Debug archive supplies formatting/clock helpers outside the hot parser-call loop.

Sources and evidence:

- [Three-line timezone patch](candidates/tz_fastpath.patch), [weekday-length patch](candidates/weekday_lengths.patch).
- [All 1,488 summary rows with ns/call and intervals](recorded-results/work-reduction/summary.csv), [30,240 raw workload pairs](recorded-results/work-reduction/raw.csv), [720 original parser pairs](recorded-results/work-reduction/perf.csv).
- [Assembly metrics](recorded-results/work-reduction/assembly.csv), [CPU/compiler metadata](recorded-results/work-reduction/environments.json), [run/job metadata](recorded-results/work-reduction/runs.json).
- [ARM summaries](recorded-results/work-reduction/arm-summary.csv), [ARM raw parser pairs](recorded-results/work-reduction/arm-perf.csv), [ARM environment](recorded-results/work-reduction/arm-environment.json).
- Rerun the manual `work-reduction.yml` workflow, then retrieve each job log and use `python3 extract.py job.log NEW_DIRECTORY`; full sources, assembly, test logs and manifests are encoded in the free logs. See [README](README.md).

No performance is guaranteed. A focused timezone PR is reviewable with these results, including its fallback regressions. Maintainer acceptance and production HTTP gains are separate questions. The earlier packed month/weekday results remain in [RESULTS.md](RESULTS.md). Follow-up source review of other projects is in [FOLLOWUP-CANDIDATES.md](FOLLOWUP-CANDIDATES.md).
