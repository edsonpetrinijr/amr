import collections

PATH = r"C:\Users\junioeg\robotics\robotics1\TRANVR2.TXT"

PEDIDO = {"IKS","I5F","N5F","NFM","NKS","NS3","I5U","I5T","N5U"}
ATEND  = {"I6A","N6A","N6K","N6L","N6J","N9U"}   # consumo real / baixa

def F(raw):
    return (raw[0:3].strip(), raw[6:13].strip(), raw[14:20].strip(),
            raw[29:35].strip(), raw[35:44].strip())

atend  = collections.Counter()
pedido = collections.Counter()
parts  = collections.defaultdict(set)
pou_ct = collections.defaultdict(collections.Counter)   # cell -> POU -> count (atend)
sloc_ct= collections.defaultdict(collections.Counter)   # cell -> storage_loc -> count

with open(PATH, "r", encoding="latin-1", errors="replace") as fh:
    for line in fh:
        if not line.strip():
            continue
        rt, part, sloc, cell, pou = F(line)
        if not cell.startswith("BT"):     # transmission building
            continue
        if rt in ATEND:
            atend[cell] += 1
            if part: parts[cell].add(part)
            if pou:  pou_ct[cell][pou] += 1
            if sloc: sloc_ct[cell][sloc] += 1
        elif rt in PEDIDO:
            pedido[cell] += 1
            if part: parts[cell].add(part)

print("=== CÉLULAS DA TRANSMISSÃO (cell começa com 'BT'), ranqueadas por ATENDIMENTO (I6A=consumo real) ===")
print(f"{'CELL':8}{'ATEND':>6}{'PEDIDO':>7}{'#PART':>6}{'#POU':>5}  {'POU_dom(%)':>14}  {'SLOC_dom(%)':>14}")
for c, n in atend.most_common(30):
    npou = len(pou_ct[c])
    if pou_ct[c]:
        pou_d, pou_n = pou_ct[c].most_common(1)[0]
        pou_share = 100*pou_n/sum(pou_ct[c].values())
        pou_s = f"{pou_d}({pou_share:.0f}%)"
    else:
        pou_s = "-(sem POU)"
    if sloc_ct[c]:
        sl_d, sl_n = sloc_ct[c].most_common(1)[0]
        sl_share = 100*sl_n/sum(sloc_ct[c].values())
        sl_s = f"{sl_d}({sl_share:.0f}%)"
    else:
        sl_s = "-"
    print(f"{c:8}{n:6d}{pedido[c]:7d}{len(parts[c]):6d}{npou:5d}  {pou_s:>14}  {sl_s:>14}")
