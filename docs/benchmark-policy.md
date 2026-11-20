# Benchmark policy

This repository is an engineering learning project, not a performance leaderboard.

- Specify the question and matching externally observable behavior before implementation.
- Keep workloads equivalent where practical; explicitly document semantic differences.
- Build applications before measurements; avoid charging compilation to one runtime.
- Run on the same host under similar load; alternate test order and record runtime versions.
- Record raw trials with environment, parameters, exact commands, and dates.
- Report medians and dispersion, not only best results; inspect correctness before speed.
- Use memory, tail latency, saturation, and failure measurements only when instrumented.
- Do not equate goroutines with BEAM processes or Go panic recovery with OTP supervision.
- Do not infer real-world production performance from synthetic microbenchmarks.
- Don't commit made-up results. Review raw evidence before adding summaries.

Articles are written and published outside this repository. Link to specific commit SHAs when citing results.
