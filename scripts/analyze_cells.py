import collections, sys

PATH = r"C:\Users\junioeg\robotics\robotics1\TRANVR2.TXT"

# Transaction dictionary (from founder's official dictionary)
PEDIDO   = {"IKS","I5F","N5F","NFM","NKS","NS3","I5U","I5T","N5U"}  # solicitations / moves
ATEND    = {"I6A","N6A","N6K","N6L","N6J","N9U"}                    # atendimento = real consumption/baixa
CANCEL   = {"I7Q","N02","N7A","N7V"}

def fields(raw):
    return dict(
        rt   = raw[0:3].strip(),
        part = raw[6:13].strip(),
        sloc = raw[14:20].strip(),
        cell = raw[29:35].strip(),
        pou  = raw[35:44].strip(),
        qty  = raw[44:53].strip(),
    )

cell_atend   = collections.Counter()     # I6A-type events per cell
cell_pedido  = collections.Counter()     # pedido events per cell
cell_parts   = collections.defaultdict(set)
cell_pous    = collections.defaultdict(set)
rt_counter   = collections.Counter()
total = 0

with open(PATH, "r", encoding="latin-1", errors="replace") as fh:
    for line in fh:
        if not line.strip():
            continue
        total += 1
        f = fields(line)
        rt_counter[f["rt"]] += 1
        c = f["cell"]
        if not c:
            continue
        if f["rt"] in ATEND:
            cell_atend[c] += 1
            if f["part"]: cell_parts[c].add(f["part"])
            if f["pou"]:  cell_pous[c].add(f["pou"])
        elif f["rt"] in PEDIDO:
            cell_pedido[c] += 1
            if f["part"]: cell_parts[c].add(f["part"])
            if f["pou"]:  cell_pous[c].add(f["pou"])

print(f"TOTAL LINES: {total}")
print(f"DISTINCT CELLS (any): {len(set(list(cell_atend)+list(cell_pedido)))}")
print()
print("=== TOP 25 CÉLULAS POR ATENDIMENTO (I6A-type = consumo real) ===")
print(f"{'CELL':8} {'ATEND':>6} {'PEDIDO':>7} {'#PART':>6} {'#POU':>5}  POUs(amostra)")
for c, n in cell_atend.most_common(25):
    pous = sorted(cell_pous[c])
    sample = ",".join(pous[:3]) + ("..." if len(pous) > 3 else "")
    print(f"{c:8} {n:6d} {cell_pedido[c]:7d} {len(cell_parts[c]):6d} {len(cell_pous[c]):5d}  {sample}")
