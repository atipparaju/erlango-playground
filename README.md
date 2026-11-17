# Erlango Playground

Reproducible, use-case-driven experiments comparing Erlang/OTP and Go.

Each use case includes equivalent Go and Erlang examples, a reproducible experiment harness, and recorded results (when verified). The goal is to study engineering trade-offs, **not** to declare a universal language winner.

## Conventions

- `usecases/<number>-<topic>/go/`: standalone Go implementation.
- `usecases/<number>-<topic>/erlang/`: equivalent Erlang/OTP implementation.
- `usecases/<number>-<topic>/experiments/`: benchmark runners, raw outputs, and methodology.
- `usecases/<number>-<topic>/README.md`: contracts, commands, and interpretation.
- `docs/`: shared experiment and comparison guidance.

Benchmarks must record runtime versions, hardware, parameters, repetitions, and raw evidence. Numbers are not published until actually measured. No external article manuscript belongs in this repository.

## Use cases

| Use case | Topic | Status |
|---|---|---|
| 01 | State ownership and message passing | In development |

## Publishing

Articles and essays are maintained separately from this repository. This repo contains only code, technical notes, scripts, and reproducible evidence.
