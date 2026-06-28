#!/usr/bin/env python3
# Generate the LC method-map bipartite SVG (standalone, hardcoded colors + white bg).
import html, os

# ---- data ----
# blocks in current order; (letter, cn, en, is_family) family=stack/heap cluster E,F,G
blocks = [
    ("A","求最优","optimize",False),
    ("B","找/定位","locate",False),
    ("C","枚举","enumerate",False),
    ("D","计数","count",False),
    ("E","第k","k-th",True),
    ("F","顺序/依赖","order",True),
    ("G","匹配/解析","match·parse",True),
    ("H","分组/连通","group",False),
    ("I","遍历产出","traverse",False),
    ("J","字符串","string",False),
    ("K","子数组和","prefix-sum",False),
]
# tasks: (block, label, ds, num, algo_id)
tasks = [
    ("A","Longest substring w/ a condition","arr/str","3","SW"),
    ("A","Minimize the max / smallest feasible","answer space","875","BinSearch"),
    ("A","Fewest steps, unweighted graph/2D","graph/2D","1091","BFS"),
    ("A","Cheapest path through a 2D array","2D array","64","DP"),
    ("A","Best buy-sell profit, one sweep","array","121","DP"),
    ("A","Best over a sequence, overlap subs","arr/str","322","DP"),
    ("B","Find target in a sorted array","sorted","704","BinSearch"),
    ("B","Find a pair summing to target","sorted","167","TwoPtr"),
    ("B","Detect a cycle / find duplicate","list/array","287","FastSlow"),
    ("C","List all subsets / permutations","decision tree","78","Backtrack"),
    ("C","Search all paths in a 2D array","2D array","79","Backtrack"),
    ("D","Count how many ways / paths","arr/2D/str","62","DP"),
    ("E","K-th largest / smallest (static)","array","215","Heap"),
    ("E","K-th / median in a stream","stream","295","Heap"),
    ("F","Next greater / smaller element","array","739","MonoStack"),
    ("F","Prerequisite / build order","graph DAG","207","Topo"),
    ("G","Parse / validate a nested structure","stack","394","Stack"),
    ("H","Connected components / islands","graph/2D","200","BFS"),
    ("H","Merge overlapping intervals","intervals","56","Sweep"),
    ("I","Output a 2D array in spiral order","2D array","54","Sim"),
    ("I","Binary tree level/pre/in/post order","tree","102","BFS"),
    ("J","Prefix / dictionary lookup","string set","208","Trie"),
    ("J","Longest palindrome","string","5","Expand"),
    ("K","Subarray sum equals k","array","560","Prefix"),
]
# algorithms: id -> (label, is_hub)
algos = {
    "SW":("Sliding window",False), "BinSearch":("Binary search ★",True),
    "BFS":("BFS / DFS ★",True), "DP":("DP ★",True), "TwoPtr":("Two pointers",False),
    "FastSlow":("Fast-slow pointers",False), "Backtrack":("Backtracking ★",True),
    "Heap":("Heap",False), "MonoStack":("Monotonic stack",False),
    "Topo":("Topological sort",False), "Stack":("Stack",False),
    "Sweep":("Sort + sweep",False), "Sim":("Simulation",False), "Trie":("Trie",False),
    "Expand":("Expand-center / DP",False), "Prefix":("Prefix + hash",False),
}

# ---- layout ----
RH=27; TOP=24
gx0,gx1=3,95          # gutter (block letter + title); widened, stealing from the roomy algo column
cx0=100; cw=272; cx1=cx0+cw  # left cells -> right edge 372
ax0=486; aw=268; ax1=ax0+aw  # right algos -> right edge 754
lx0=cx1; lx1=ax0             # line span
W=760
n=len(tasks)
bottom=TOP+n*RH
H=bottom+34

def row_cy(i): return TOP+i*RH+RH/2

# algo vertical positions: order by avg source-row, even spacing
src={k:[] for k in algos}
for i,(b,lab,ds,num,a) in enumerate(tasks): src[a].append(i)
order=sorted(algos.keys(), key=lambda k: sum(src[k])/len(src[k]) if src[k] else 0)
ay0=TOP+8; ay1=bottom-8
ays={}
for j,k in enumerate(order):
    ays[k]=ay0+(ay1-ay0)*j/(len(order)-1)

# colors
BG="#ffffff"
CELL="#ffffff"; CELLB="#D6D4CB"; TXT="#2C2C2A"; NUM="#185FA5"; DS="#8A8980"
BARD="#ECEAE2"; BARF="#E1EEFB"; BARB="#C9C7BD"; BART="#5F5E5A"
HUBF="#E1EEFB"; HUBB="#185FA5"; HUBT="#0C447C"
LEAFF="#F1EFE8"; LEAFB="#B7B5AB"; LEAFT="#444441"
LHUB="#3D8BDC"; LLEAF="#AFAEA6"

def esc(s): return html.escape(s, quote=True)

svg=[]
svg.append(f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" font-family="-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif">')
svg.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="{BG}"/>')

# lines first (under nodes)
for i,(b,lab,ds,num,a) in enumerate(tasks):
    y1=row_cy(i); y2=ays[a]; hub=algos[a][1]
    col=LHUB if hub else LLEAF; wdt=1.7 if hub else 1.0
    mx=(lx0+lx1)/2
    svg.append(f'<path d="M {lx0} {y1:.1f} C {mx} {y1:.1f} {mx} {y2:.1f} {lx0+ (lx1-lx0)} {y2:.1f}" fill="none" stroke="{col}" stroke-width="{wdt}" opacity="0.6"/>')

# block bars (gutter)
# compute block row ranges
brange={}
for i,(b,*_ ) in enumerate(tasks):
    brange.setdefault(b,[i,i]); brange[b][1]=i
for (letter,cn,en,fam) in blocks:
    a,bb=brange[letter]
    yt=TOP+a*RH+2; hh=(bb-a+1)*RH-4
    fill=BARF if fam else BARD
    svg.append(f'<rect x="{gx0}" y="{yt}" width="{gx1-gx0}" height="{hh}" rx="4" fill="{fill}" stroke="{BARB}" stroke-width="0.8"/>')
    cy=yt+hh/2
    svg.append(f'<text x="{(gx0+gx1)/2:.1f}" y="{cy:.1f}" text-anchor="middle" dominant-baseline="central" font-size="10.5" fill="{BART}"><tspan font-weight="700" font-size="12">{letter}</tspan> {esc(cn)}</text>')

# left cells
for i,(b,lab,ds,num,a) in enumerate(tasks):
    yt=TOP+i*RH+2; hh=RH-4; cy=row_cy(i)
    svg.append(f'<rect x="{cx0}" y="{yt}" width="{cw}" height="{hh}" rx="3" fill="{CELL}" stroke="{CELLB}" stroke-width="0.8"/>')
    svg.append(f'<text x="{cx0+7}" y="{cy+1:.0f}" font-size="10.5" fill="{TXT}">{esc(lab)}<tspan fill="{DS}" font-size="9.5"> · {esc(ds)}</tspan></text>')
    svg.append(f'<text x="{cx1-7}" y="{cy+1:.0f}" text-anchor="end" font-size="10.5" font-weight="600" fill="{NUM}">#{num}</text>')

# right algo nodes
ah=24
for k in order:
    lab,hub=algos[k]; cyc=ays[k]; yt=cyc-ah/2
    f,bcol,tcol=(HUBF,HUBB,HUBT) if hub else (LEAFF,LEAFB,LEAFT)
    bw=1.6 if hub else 0.8
    svg.append(f'<rect x="{ax0}" y="{yt:.1f}" width="{aw}" height="{ah}" rx="4" fill="{f}" stroke="{bcol}" stroke-width="{bw}"/>')
    fw="600" if hub else "400"
    svg.append(f'<text x="{ax0+10}" y="{cyc+1:.1f}" font-size="11" font-weight="{fw}" fill="{tcol}">{esc(lab)}</text>')

# legend
ly=H-12
svg.append(f'<text x="{gx0}" y="{ly}" font-size="10" fill="{LEAFT}">蓝框=枢纽算法(收多条线) · 灰框=叶子算法(1:1) · 左侧 A–K 意图 block,蓝条 E·F·G=栈/堆同族</text>')

svg.append('</svg>')

out=os.path.expanduser("~/cs-resources/images/method-map.svg")
os.makedirs(os.path.dirname(out),exist_ok=True)
with open(out,"w") as f: f.write("\n".join(svg))
print("wrote",out,"rows",n,"H",H)
