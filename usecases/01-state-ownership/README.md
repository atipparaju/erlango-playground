# Use case 01: State ownership through message passing

## Question

When many clients update one logical counter, what are the costs and benefits of giving one process/goroutine exclusive ownership of state, rather than sharing mutable state?

This experiment compares **one Go goroutine owning a counter** with **one Erlang/OTP gen_server owning a counter**. Both accept synchronous increments and check the final value.

## Structure

- `go/` — Go standalone command and tests.
- `erlang/` — Erlang gen_server and command-line runner.
- `experiments/run.py` — matched trial execution; raw evidence saved as JSON Lines.
- `experiments/results/` — place reproducible measurements here; no measurements are claimed yet.

## Run

Requirements: Go >= 1.22, Erlang/OTP with `erl` and `erlc`, Python >= 3.9.

```bash
cd usecases/01-state-ownership/go
go test ./...
go run . -clients 4 -ops 10000 -mailbox 0
```

```bash
cd usecases/01-state-ownership/erlang
erlc counter_bench.erl
erl -noshell -pa . -s counter_bench main -extra 4 10000
```

From repository root:

```bash
python3 usecases/01-state-ownership/experiments/run.py --clients 4 --ops 10000 --repetitions 5
```

The experiment runner compiles both examples ahead of execution, alternates language order between trials, and writes raw JSONL results.

## Semantics and limitations

1. **Single state owner:** both implementations serialize updates at one owner. This is intentionally a potential bottleneck, not a horizontally scalable counter.
2. **Synchronous operations:** clients wait for a reply before sending another increment, bounding the number of in-flight requests by the number of clients.
3. **Different mailboxes:** Go uses a channel (capacity configurable, default 0); Erlang gen_server has a process mailbox without the same fixed capacity. Matching application-level in-flight demand does **not** imply identical runtime mailbox behavior.
4. **Different failure semantics:** BEAM process isolation is not equivalent to Go goroutine isolation. This experiment does not test supervision, recovery, or fatal faults.
5. **Timing:** wall-clock elapsed time encompasses client scheduling and calls but excludes compilation and server startup. The recorded requests-per-second value is a workload throughput measure, **not** a universal language-speed comparison.
6. **Limitations:** a single host, runtime defaults, runtime JIT/warm-up effects, and small example workloads can materially affect results. Use multiple input sizes and repeat runs; retain raw outputs and avoid unsupported performance claims.
7. **Memory:** no comparable memory measurement is provided in this first version; do not infer memory-efficiency conclusions from throughput.

## Suggested study matrix

Run with 1, 4, 16, and 64 clients and 1000, 10000, and 100000 increments per client. Repeat at least five times and report median and distribution of results. Capture exact CPU, RAM, OS, Erlang/OTP, Go versions, and whether thermal throttling was present.

## Next questions

- How does a bounded/overloaded mailbox affect latency and fairness?
- How should per-entity state be sharded across multiple owners?
- How does OTP supervision compare with explicit Go worker recovery?
- How do actor-style designs compare to idiomatic Go mutex-protected counters?
