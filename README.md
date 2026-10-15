# Free native x86 curl date benchmark

Completed native runs: [results and CPU comparisons](RESULTS.md).

Manual GitHub Actions workflow for a **public** benchmark repository. No upstream curl pull request is created. It compares current-master baseline `653f7d7fa983938c4c9331d14c71bc9fa5a5aba8` with portable three-byte and two-byte packed weekday/month lookups. Candidate snapshots and the same added unit4781 edge cases are included under curl's license. All benchmark source is inspectable before publication.

## What runs

- Standard `ubuntu-24.04` x86-64 runners, three independent VM replicates. Private-repository jobs are explicitly skipped.
- GCC14 and Clang17 at O2 and O3. CPU model, actual compiler versions, allowed CPU affinity, configuration and exact commands are recorded.
- All available curl unit tests and21 selected date-related HTTP/FTP/unit cases against baseline and both candidates, before timing.
- All256^3 byte triplets, exact-size and short buffers, complete weekday case variants, the183-date curl corpus and100,000 random ASCII parser inputs; Clang ASan/UBSan plus forced unsigned-char. Parse-disabled translation units are compiled in each compiler/optimization configuration. Full disabled curl builds were already tested on the local ARM64 host; this workflow does not claim to repeat those full disabled builds.
- Isolated valid/invalid/short/near-miss/wrong-first-character lookups and complete parser workloads:21 randomized paired rounds per workload. The18 workloads use1,024-entry reproducible datasets repeated256 times per sample.
- Curl's original unmodified complete-parser benchmark:15 paired samples,20,000 passes over183 dates each. Every candidate is compared against baseline within the same VM, with pair order shuffled. Timed executables are pinned to one allowed logical CPU. Candidate order alternates by replicate parity (a 2:1 balance across three VMs).
- Compiler assembly, disassembly, object text sizes, static instruction/branch sites, raw timings and paired bootstrap summaries. Static counts are not dynamic hardware counters.

The CMake test build is Debug with TLS disabled. Timed parser and parsing/string dependencies are independently compiled at O2/O3, without DEBUGBUILD or LTO. Formatting/clock helpers from the test archive execute outside the timed parser-call hot path. HSTS/TLS cases are outside this configuration. Feature/platform skips remain visible in logs.

## Cost controls

GitHub documents standard hosted-runner compute as free for public repositories. This workflow uses only that runner class, has a40-minute timeout per VM, and is manual-only. It creates no caches, paid artifacts, larger runners, schedules or cloud resources. Results and a compressed base64 evidence bundle are written to job logs/summary, which GitHub excludes from artifact-storage usage. There are no secrets in the workflow and its token permission is read-only.

References:
- https://docs.github.com/en/actions/reference/runners/github-hosted-runners
- https://docs.github.com/en/billing/concepts/product-billing/github-actions
- https://github.com/actions/runner-images/blob/main/images/ubuntu/Ubuntu2404-Readme.md

## Launch after choosing the public repository

Commit this directory's contents to that repository's default branch, then run:

```sh
gh workflow run date-bench.yml --repo OWNER/REPOSITORY
gh run list --repo OWNER/REPOSITORY --workflow date-bench.yml
```

The two manual workflows are `.github/workflows/date-bench.yml` and `.github/workflows/work-reduction.yml`; the workflow clones the exact benchmark commit and independently checks out the pinned curl source. It does not install or execute curl's upstream GitHub workflows.

After completion, download logs for each job separately:

```sh
gh run view RUN_ID --repo OWNER/REPOSITORY --json jobs
gh run view RUN_ID --repo OWNER/REPOSITORY --job JOB_ID --log > job.log
python3 extract.py job.log output-directory
```

`extract.py` validates the compressed bundle hash and file manifest before writing the evidence. Use a new, nonexistent output directory per job; existing directories and symlinks are refused. Inspect all three replicate environments before combining results: hosted VMs are shared infrastructure and CPU models/frequency/noisy neighbors may vary. These measurements reproduce the original architecture/compiler-major combination, not the original machine or necessarily its absolute timings.

A passing run is required before claiming x86 performance results. Local preparation checks cover Python syntax, actionlint, source hashes and extraction logic; no native x86 measurements have occurred merely by preparing this package.

No cost promise is made for modified workflows, private repositories or additional services. The checked-in workflow's public-repository guard and runner/log settings keep this experiment on the documented free path.

## Independent work-reduction experiments

`work-reduction.yml` tests `weekday_lengths` (constant suffix lengths instead of strlen) and `tz_fastpath` (exact uppercase GMT/UTC before the existing timezone search), each independently against the same pinned baseline. Run it with:

```sh
gh workflow run work-reduction.yml --repo Dueen/curl-date-benchmarks
```

This suite uses `bench-work.c`: all original 18 workloads plus 12 timezone/parser workloads, including alternate valid zones, invalid/case-sensitive names and short inputs. Verification additionally covers all 128^3 ASCII timezone triplets and 26^4 uppercase four-letter zones using exact-size allocations. There are 30 workloads and 21 paired rounds each. The original curl parser benchmark is unchanged. No speedup is assumed; compiler-, workload- and CPU-specific regressions must be reported alongside improvements.
