# Candidate for review; no upstream PR opened

Proposed title: `parsedate: bypass timezone search for GMT and UTC`

Recognize exact three-character GMT and UTC keys before searching the timezone table. Both existing entries have offset zero. Reuse MKTZ and the existing length checks; preserve all other search and case-sensitive matching behavior.

The [three-line patch](candidates/tz_fastpath.patch) applies to curl `653f7d7fa983938c4c9331d14c71bc9fa5a5aba8`. It modifies only lib/parsedate.c. The independent weekday-length experiment is excluded because it did not establish consistent complete-parser gains.

Validation: curl checksrc; 75 runnable unit tests and 21 selected date-related tests for baseline/candidate on each of six x86 VMs; exhaustive differential lookup and randomized full-parser checks; Clang ASan/UBSan with default and unsigned char; parse-disabled translation-unit compilation for GCC14/Clang17 O2/O3. Full parser timing uses curl's unmodified 183-date corpus: 15 shuffled-order baseline/candidate pairs, 20,000 corpus passes each. No full Linux parse-disabled build or TLS/HSTS test coverage is claimed.

Measured original-parser latency reductions: 0.54–4.97% across six AMD EPYC VMs and four compiler/optimization configurations; 21 of 24 within-VM descriptive intervals exclude zero. Local ARM64 follow-up with Apple Clang21/GCC16: 4.89–8.27%. These are parser benchmarks, not curl-wide throughput measurements. Intel remains untested for this patch. Generic invalid three-letter timezone lookup regressed up to 19.16%, other valid three-letter lookup up to 18.00%, and selected full-parser fallback workloads up to 2.44%. Normal parser-object text grows 16–80 bytes and gains two conditional branch sites. Hosted-runner noise and code layout remain limitations.

[Full measurements, raw paired samples and reproduction details](WORK-REDUCTION.md). A new upstream source check and maintainer review are still required before submitting or merging. Reference prior weekday/month work [curl PR #22981](https://github.com/curl/curl/pull/22981) as background; this candidate optimizes timezone recognition independently.
