import collections
PATH = r"C:\Users\junioeg\robotics\robotics1\TRANVR2.TXT"
ATEND = {"I6A","N6A","N6K","N6L","N6J","N9U"}
PEDIDO = {"IKS","I5F","N5F","NFM","NKS","NS3","I5U","I5T","N5U"}

def F(raw):
    return (raw[0:3].strip(), raw[6:13].strip(), raw[14:20].strip(),
            raw[29:35].strip(), raw[35:44].strip())

targets = ["BT09TC", "BT09SM", "BT09AS"]
pou = collections.defaultdict(collections.Counter)
sloc = collections.defaultdict(collections.Counter)
atend = collections.Counter()
pedido = collections.Counter()
parts = collections.defaultdict(set)

with open(PATH, encoding="latin-1", errors="replace") as fh:
    for line in fh:
        if not line.strip():
            continue
        rt, part, sl, cell, p = F(line)
        if cell not in targets:
            continue
        if rt in ATEND:
            atend[cell] += 1
            if part: parts[cell].add(part)
            if p: pou[cell][p] += 1
            if sl: sloc[cell][sl] += 1
        elif rt in PEDIDO:
            pedido[cell] += 1

for c in targets:
    print(f"\n=== {c} ===  atendimentos={atend[c]}  pedidos={pedido[c]}  parts={len(parts[c])}")
    print("  POU top:", pou[c].most_common(5))
    print("  SLOC top:", sloc[c].most_common(5))
