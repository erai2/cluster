#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, argparse
from pathlib import Path

RES = Path(__file__).resolve().parents[1] / "resources"
VPATH = RES / "hanja_variant_map.json"
RPATH = RES / "hanja_reading_map.json"

def main():
    ap = argparse.ArgumentParser(description="Hanja maps: show/add variants/readings")
    ap.add_argument("--show", action="store_true", help="Print current maps (head)")
    ap.add_argument("--add", nargs=2, metavar=("VARIANT","CANON"), help="Add/override variant→canon mapping")
    ap.add_argument("--reading", nargs=2, metavar=("HANJA","READING"), help="Append reading to hanja")
    args = ap.parse_args()

    VAR = json.loads(VPATH.read_text(encoding="utf-8"))
    READ = json.loads(RPATH.read_text(encoding="utf-8"))
    changed = False

    if args.add:
        v, c = args.add
        VAR[v] = c
        changed = True
        print(f"[+] mapping: {v} -> {c}")
    if args.reading:
        h, rd = args.reading
        READ.setdefault(h, [])
        if rd not in READ[h]:
            READ[h].append(rd)
            changed = True
            print(f"[+] reading: {h} += {rd}")

    if args.show or not changed:
        print("== Variant map (first 20) ==")
        for i, (k, v) in enumerate(list(VAR.items())[:20]):
            print(f"{k} -> {v}")
        print("== Reading map (first 20) ==")
        for i, (k, v) in enumerate(list(READ.items())[:20]):
            print(f"{k} -> {','.join(v)}")

    if changed:
        VPATH.write_text(json.dumps(VAR, ensure_ascii=False, indent=2), encoding="utf-8")
        RPATH.write_text(json.dumps(READ, ensure_ascii=False, indent=2), encoding="utf-8")
        print("Saved.")

if __name__ == "__main__":
    main()
