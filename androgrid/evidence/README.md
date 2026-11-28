# Measurement notes

The HTTP run was recorded on 2026-11-25 using 1 physical Pixel 8. The worker snapshot reported client version 0.0.1-alpha.5, an unrooted device, and Android 17. This is a record of that experiment, not a certification of a particular published release package.

The workload made sequential GET requests to a public HTTPS echo endpoint. The earlier submission included a concurrency variable that the inspected workload does not read. No request-concurrency claim is made.

The operator's recorded setup describes USB reverse forwarding for cluster coordination and workload delivery, with Wi-Fi for outbound test requests. That description is not a packet capture. The dashboard's transport badge describes the Android route classification and does not prove the physical path of each connection.

## Published data

- [Sanitized execution-log excerpt](execution.txt), preserving the original report's values.
- [Windows USB lab setup](windows-usb-lab.md), with review references and commands.
- [Alpha.6 wireless benchmark results](results-alpha6-wireless.json), documenting the subsequent 100% wireless onboarding run.
- [6-second illustrative workflow](../figures/03-workflow.gif), with a [static alternative](../figures/03-workflow-static.png).

The phone screenshots in the walkthrough come from the retained experiment captures. The dashboard screenshot was captured later while it still held the completed task. They do not demonstrate a new run of the reader lab. Notification bars, worker identifiers, and task identifiers are masked; no enrollment QR or pairing token is published.

[results.json](results.json) contains selected literal values from the workload's JSON report and the orchestrator's execution report. Node identifiers, task identifiers, exact event timestamps, enrollment material, and network configuration are excluded. No measurements were fabricated or generated to replace the original observations.

The workload's measurement window is 15.151075 seconds. The orchestrator reported 15,656 milliseconds for task execution. These are separate timing boundaries. Submission and scheduling latency were not measured as an end-to-end interval here.

The dashboard capture taken for this article shows the retained completed task. It is not evidence of an additional benchmark run. Published screenshot identifiers are redacted. The JSON file preserves numeric values directly from the original reports.

## Provenance and reproduction

The original report was retained by the author. The selected fields in [results.json](results.json) were extracted from that report, with identifiers and the target URL omitted. No new benchmark was run for this article. Neither a backend commit nor an APK or workload hash was recorded with the run, so the installed binaries cannot be reconstructed exactly from this package.

The implementation was checked against backend commit `53ab5e51c581358acf822cf2c651d192b6363a4b` and Android commit `e897036d91903df3dae1d821d05ad9d6846d7f31` on 2026-11-26. These are review references, not asserted build identities for the experiment. The [HTTP configuration parser](https://github.com/ligature-platform/androgrid-backend/blob/53ab5e51c581358acf822cf2c651d192b6363a4b/workloads/http-benchmark/src/config.rs) and [request loop](https://github.com/ligature-platform/androgrid-backend/blob/53ab5e51c581358acf822cf2c651d192b6363a4b/workloads/http-benchmark/src/engine.rs) establish the sequential request model in the reviewed implementation.

## Limits

The experiment contains 76 requests from 1 phone. It does not establish maximum throughput, multi-device scaling, wireless enrollment, cellular energy behavior, memory-leak freedom, sustained thermal behavior, or a comparative cost/performance advantage. Latency percentiles describe this small sample only; no cause is assigned to outliers.

### Subsequent validation: 100% wireless onboarding in v0.0.1-alpha.6
On 2026-11-28, the wireless onboarding and reverse-tunnel limitation was investigated and resolved (Issue #30, Gate L-02). Validation on the same physical Google Pixel 8 running `v0.0.1-alpha.6` demonstrated 100% wireless onboarding, certificate enrollment, artifact fetching, and benchmark execution (79 requests, 0 errors, 100% success rate, 5.26 req/s) over physical Wi-Fi LAN with zero active USB reverse tunnels (`adb reverse --list` verified empty). See [results-alpha6-wireless.json](results-alpha6-wireless.json) for the sanitized run data.

For a repeatable performance comparison, record the exact backend/APK/workload identities and hashes, use a controlled target with permission, repeat runs, and preserve workload inputs and outputs. Verify returned output against an independent expectation. Keep originals outside the public publication package when they contain credentials or device identifiers.

## Source and further reading

- [HTTP workload source](https://github.com/ligature-platform/androgrid-backend/tree/main/workloads/http-benchmark)
- [Project documentation](https://ligature-platform.github.io/androgrid-backend/)
- [Article](../)

Documentation and source on the default branch can evolve after this article. Reproduction needs a compatible selected build and its current instructions.
