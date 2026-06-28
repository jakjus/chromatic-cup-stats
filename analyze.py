import json, math
from collections import defaultdict, Counter

with open('tournament_data.json') as f:
    data = json.load(f)

NAME_MERGES = {
    "jakjus": "jakjus", "trozz": "Trozz", "gsvalhalla": "GSValhalla",
    "freezard": "Freezard", "ghosterdriver": "Ghosterdriver",
    "subini": "Subini", "meziljie": "Meziljie", "pasty": "Pasty",
    "zaow": "Zaow", "catpaw": "Catpaw",
    "szenszej": "szenszej", "szenszej_": "szenszej",
    "bagofshittyoranges": "BagofShittyOranges",
    "huevosexplosivo": "Catpaw", "huevosexplosivos": "Catpaw", "huevosexplosivo(catpaw)": "Catpaw",
    "renedave (100line)": "renedave", "renedave(100line)": "renedave",
    "oats": "buyingcoats", "buyingcoats": "buyingcoats", "atrum": "atrum",
    "shatteredglass": "ShatteredGlass",
    "shatteredglass (invitation pending)": "ShatteredGlass",
    "abracadani": "abracadani", "demmiremmi": "Demmiremmi",
    "prisonpriest": "prisonpriest", "rocken": "Rocken", "ibes": "Ibes",
    "confirmedharry212": "ConfirmedHarry212", "confirmed harry": "ConfirmedHarry212",
    "sm1les": "sm1les", "madwhiffery": "madwhiffery", "xenoce": "Xenoce",
    "p3p0": "p3P0", "andreios": "Andreios", "smarty": "Smarty",
    "incognito": "incognito", "scuttle": "Scuttle", "joseph990": "joseph990",
    "pkp": "pkp", "cody": "Cody", "kieran": "Kieran", "calvin": "calvin",
    "fainr": "Fainr", "baldeaglepc": "BaldEaglePC", "solarpie": "SolarPie",
    "zerounderscoreou": "ZeroUnderscoreOu", "fylgjaapologist": "FylgjaApologist",
    "moby1981": "moby1981", "welcomebackgeneral": "welcomebackgeneral",
    "paks": "Paks", "coccolithophor": "Coccolithophor", "knightality": "Knightality",
    "aestari": "aestari", "egganimal": "EggAnimal", "abcd": "buyingcoats",
    "bazilikoviichai": "BazilikoviiChai", "bazilkovichai": "BazilikoviiChai", "bazilikoviiichai": "BazilikoviiChai",
    "looniewho": "LoonieWho", "c91": "C91",
}

all_raw_names = set()
for td in data.values():
    for name in td['players'].values():
        all_raw_names.add(name)

canonical_map = {}
for name in sorted(all_raw_names):
    lower = name.lower().strip()
    canonical_map[lower] = NAME_MERGES.get(lower, name)

def normalize(name):
    return canonical_map.get(name.lower().strip(), name)

stats = defaultdict(lambda: {"wins":0,"losses":0,"tourneys":set(),"wins_count":0})
records = defaultdict(list)
winner_count = Counter()

for num in sorted(data.keys(), key=int):
    td = data[num]
    for pid, raw_name in td['players'].items():
        name = normalize(raw_name)
        w = td['win_counts'].get(pid, 0)
        l = td['loss_counts'].get(pid, 0)
        pl = td['placements'].get(pid, 99)
        stats[name]["wins"] += w
        stats[name]["losses"] += l
        stats[name]["tourneys"].add(int(num))
        if pid == td['winner_id']:
            stats[name]["wins_count"] += 1
            winner_count[name] += 1
        records[name].append({'num':int(num),'wins':w,'losses':l,'placement':pl,'total_players':td['total_players']})

print("=" * 72)
print("1. TOURNAMENT WINNERS")
print("=" * 72)
for p, c in winner_count.most_common():
    print(f"  {p:28s} {c}")

print("\n" + "=" * 72)
print("2. MATCH WIN RATIO (min 3 matches)")
print("=" * 72)
ratios = []
for p, s in stats.items():
    t = s["wins"] + s["losses"]
    if t >= 3:
        ratios.append((p, s["wins"]/t, s["wins"], s["losses"], t))
ratios.sort(key=lambda x: (-x[1], -x[2]))
print(f"  {'Player':28s} {'Ratio':>6s} {'W':>3s} {'L':>3s} {'Total':>5s}")
for p, r, w, l, t in ratios[:20]:
    print(f"  {p:28s} {r:6.2%} {w:3d} {l:3d} {t:5d}")

print("\n" + "=" * 72)
print("3. TOURNAMENT WIN RATIO (min 2 tourneys)")
print("=" * 72)
t_ratios = []
for p, s in stats.items():
    played = len(s["tourneys"])
    won = s["wins_count"]
    if played >= 2:
        t_ratios.append((p, won/played, won, played))
t_ratios.sort(key=lambda x: (-x[1], -x[2]))
print(f"  {'Player':28s} {'Ratio':>6s} {'Won':>3s} {'Played':>6s}")
for p, r, won, played in t_ratios[:15]:
    print(f"  {p:28s} {r:6.2%} {won:3d} {played:6d}")

print("\n" + "=" * 72)
print("4. POINTS (Top 20)")
print("=" * 72)
print("  Base: 1st=100 2nd=60 3rd=40 4th=25 5-8=15 9-16=8 17+=5")
print("  Scaled by (1 + log2(players/4))")
print()
pts = defaultdict(float)
for name, recs in records.items():
    for rec in recs:
        pl = rec['placement']
        sf = 1 + math.log2(max(rec['total_players']/4, 1))
        bp = {1:100, 2:60, 3:40, 4:25}.get(pl, 15 if pl <= 8 else 8 if pl <= 16 else 5)
        pts[name] += round(bp * sf, 1)

ranked = sorted(pts.items(), key=lambda x: -x[1])
print(f"  {'Rank':>4s} {'Player':28s} {'Points':>8s} {'T':>3s}")
for i, (p, v) in enumerate(ranked[:20], 1):
    print(f"  {i:4d} {p:28s} {v:8.1f} {len(stats[p]['tourneys']):3d}")
