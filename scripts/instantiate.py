#!/usr/bin/env python3
"""Reference implementation of the twa-template instantiation contract.

play-publisher performs the same substitution; this script is the executable
spec + the smoke-test helper. It replaces every {{TOKEN}} across the Android
project with concrete values, then fails loudly if any token is left over or
any provided key is not part of the contract.

Usage:
    python3 scripts/instantiate.py --sample            # build-verify with dummy values
    python3 scripts/instantiate.py --values values.json # real instantiation
"""
from __future__ import annotations
import argparse, json, os, re, sys

# The contract. Keys here == the {{TOKEN}} names documented in README.md.
CONTRACT = [
    "APP_ID", "APP_NAME", "LAUNCHER_NAME", "HOST", "START_URL",
    "THEME_COLOR", "BACKGROUND_COLOR", "NAV_COLOR",
    "ICON_URL", "MASKABLE_ICON_URL", "MONOCHROME_ICON_URL",
    "VERSION_NAME", "VERSION_CODE", "SHA256_FINGERPRINT",
]

SAMPLE = {
    "APP_ID": "xyz.mdhv.sample", "APP_NAME": "Sample App", "LAUNCHER_NAME": "Sample",
    "HOST": "app.example.com", "START_URL": "https://app.example.com/",
    "THEME_COLOR": "#0B0B0F", "BACKGROUND_COLOR": "#0B0B0F", "NAV_COLOR": "#0B0B0F",
    "ICON_URL": "https://app.example.com/icon-512.png",
    "MASKABLE_ICON_URL": "https://app.example.com/icon-512.png",
    "MONOCHROME_ICON_URL": "https://app.example.com/icon-mono.png",
    "VERSION_NAME": "1.0.0", "VERSION_CODE": "1", "SHA256_FINGERPRINT": "AB:CD:EF",
}

# Files/dirs whose {{TOKEN}}s get substituted (NOT scripts/ or README — those document tokens).
TARGET_DIRS = ["app", ".well-known"]
TARGET_FILES = ["twa-manifest.json"]
TOKEN = re.compile(r"\{\{([A-Z_]+)\}\}")


def target_files(root: str):
    for f in TARGET_FILES:
        p = os.path.join(root, f)
        if os.path.isfile(p):
            yield p
    for d in TARGET_DIRS:
        for dp, _, files in os.walk(os.path.join(root, d)):
            for f in files:
                yield os.path.join(dp, f)


def main() -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--sample", action="store_true")
    g.add_argument("--values", metavar="values.json")
    ap.add_argument("--root", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    args = ap.parse_args()

    values = dict(SAMPLE) if args.sample else json.load(open(args.values))

    missing = [k for k in CONTRACT if k not in values]
    extra = [k for k in values if k not in CONTRACT]
    if missing:
        print(f"ERROR: missing contract tokens: {missing}", file=sys.stderr); return 2
    if extra:
        print(f"ERROR: values contain non-contract keys: {extra}", file=sys.stderr); return 2

    left: set[str] = set()
    unknown: set[str] = set()
    for p in target_files(args.root):
        s = open(p, encoding="utf-8").read()
        if "{{" not in s:
            continue

        def repl(m: re.Match) -> str:
            k = m.group(1)
            if k not in values:
                unknown.add(k); return m.group(0)
            return values[k]

        open(p, "w", encoding="utf-8").write(TOKEN.sub(repl, s))

    # Verify nothing left un-substituted.
    for p in target_files(args.root):
        for m in TOKEN.finditer(open(p, encoding="utf-8").read()):
            left.add(m.group(1))
    if unknown:
        print(f"ERROR: undocumented tokens in tree: {sorted(unknown)}", file=sys.stderr); return 3
    if left:
        print(f"ERROR: tokens left un-substituted: {sorted(left)}", file=sys.stderr); return 3

    print(f"Instantiated with {'sample' if args.sample else args.values} values — 0 tokens remaining.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
