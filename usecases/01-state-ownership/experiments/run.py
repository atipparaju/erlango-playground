#!/usr/bin/env python3
"""Run matched Go/Erlang trials; retain raw evidence rather than declaring a winner."""
import argparse
import json
import os
import platform
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def cmd(args, cwd=None):
    return subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--clients", type=int, default=4)
    parser.add_argument("--ops", type=int, default=10000)
    parser.add_argument("--repetitions", type=int, default=5)
    parser.add_argument("--mailbox", type=int, default=0, help="Go channel buffer; default 0")
    parser.add_argument("--output", type=Path, default=ROOT / "experiments" / "results" / "raw.jsonl")
    args = parser.parse_args()
    if args.clients < 1 or args.ops < 1 or args.repetitions < 1 or args.mailbox < 0:
        parser.error("clients, ops, repetitions must be positive; mailbox must be non-negative")
    for exe in ("go", "erl", "erlc"):
        if not shutil.which(exe):
            parser.error(f"missing executable: {exe}")
    metadata = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "host": platform.platform(),
        "machine": platform.machine(),
        "cpu_count": os.cpu_count(),
        "go_version": cmd(["go", "version"]),
        "otp_release": cmd(["erl", "-noshell", "-eval",
                            'io:format("~s", [erlang:system_info(otp_release)]), halt().']),
        "clients": args.clients,
        "ops_per_client": args.ops,
        "repetitions": args.repetitions,
        "go_mailbox_capacity": args.mailbox,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as directory:
        erlang = ROOT / "erlang" / "counter_bench.erl"
        cmd(["erlc", "-o", directory, str(erlang)])
        # Build before timing to exclude compilation from application timing.
        go_bin = Path(directory) / "counter-go"
        cmd(["go", "build", "-o", str(go_bin), "."], cwd=ROOT / "go")
        with args.output.open("w", encoding="utf-8") as out:
            for trial in range(args.repetitions):
                # Alternate the order to reduce systematic first-run advantage.
                langs = ["go", "erlang"] if trial % 2 == 0 else ["erlang", "go"]
                for lang in langs:
                    if lang == "go":
                        invocation = [str(go_bin), "-clients", str(args.clients),
                                      "-ops", str(args.ops), "-mailbox", str(args.mailbox)]
                    else:
                        invocation = ["erl", "-noshell", "-pa", directory,
                                      "-s", "counter_bench", "main", "-extra",
                                      str(args.clients), str(args.ops)]
                    result = json.loads(cmd(invocation))
                    row = {"metadata": metadata, "trial": trial + 1, **result}
                    out.write(json.dumps(row) + "\n")
                    out.flush()
                    print(f"trial={trial+1} language={lang} ops/s={result['ops_per_second']:.1f}")
    print(f"raw evidence: {args.output}")

if __name__ == "__main__":
    main()
