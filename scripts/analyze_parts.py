import collections, sys

PATH = r"C:\Users\junioeg\robotics\amr\TRANVR2.TXT"
TARGETS = {"3679579", "4175193", "3989602"}

ATEND = {"I6A", "N6A", "N6K", "N6L", "N6J", "N9U"}
PEDIDO = {"IKS", "I5F", "N5F", "NFM", "NKS", "NS3", "I5U", "I5T", "N5U"}

def F(raw):
    return (
        raw[0:3].strip(),    # record_type
        raw[6:13].strip(),   # part_number
        raw[14:20].strip(),  # storage_loc (pickup)
        raw[29:35].strip(),  # cell
        raw[35:44].strip(),  # pou (dropoff)
        raw[44:53].strip(),  # quantity
        raw[78:88].strip(),  # date
    )

stats = {p: {
    "rt": collections.Counter(),
    "atend": 0, "pedido": 0, "other": 0,
    "cells": collections.Counter(),
    "pou": collections.Counter(),
    "sloc": collections.Counter(),
    "atend_cells": collections.Counter(),
    "atend_pou": collections.Counter(),
    "atend_sloc": collections.Counter(),
    "dates": [],
    "qty_total": 0,
} for p in TARGETS}

with open(PATH, encoding="latin-1", errors="replace") as fh:
    for line in fh:
        if not line.strip():
            continue
        rt, part, sl, cell, pou, qty, date = F(line)
        if part not in TARGETS:
            continue
        s = stats[part]
        s["rt"][rt] += 1
        if cell: s["cells"][cell] += 1
        if pou: s["pou"][pou] += 1
        if sl: s["sloc"][sl] += 1
        if date: s["dates"].append(date)
        if rt in ATEND:
            s["atend"] += 1
            if cell: s["atend_cells"][cell] += 1
            if pou: s["atend_pou"][pou] += 1
            if sl: s["atend_sloc"][sl] += 1
            try: s["qty_total"] += float(qty)
            except: pass
        elif rt in PEDIDO:
            s["pedido"] += 1
        else:
            s["other"] += 1

for p in ["3679579", "4175193", "3989602"]:
    s = stats[p]
    total = sum(s["rt"].values())
    print("=" * 70)
    print(f"PART {p}  | total registros={total}  atend={s['atend']}  pedido={s['pedido']}  outros={s['other']}")
    if s["dates"]:
        ds = sorted(s["dates"])
        print(f"  periodo: {ds[0]} -> {ds[-1]}   qty_total_atend={s['qty_total']:.0f}")
    print(f"  tipos de transacao: {dict(s['rt'].most_common())}")
    print(f"  --- TODOS os registros ---")
    print(f"  celulas:     {s['cells'].most_common(8)}")
    print(f"  POU(dropoff):{s['pou'].most_common(8)}")
    print(f"  SLOC(pickup):{s['sloc'].most_common(8)}")
    print(f"  --- so ATENDIMENTOS (consumo real) ---")
    print(f"  celulas:     {s['atend_cells'].most_common(8)}")
    print(f"  POU(dropoff):{s['atend_pou'].most_common(8)}")
    print(f"  SLOC(pickup):{s['atend_sloc'].most_common(8)}")
    print()
