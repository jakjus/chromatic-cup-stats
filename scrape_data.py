import cloudscraper, json, re, time, math
from collections import defaultdict, Counter

scraper = cloudscraper.create_scraper()

tournament_slugs = {
    1: 'chrocup1', 2: 'chrocup2', 3: 'chrocup3', 4: 'chrocup4', 5: 'chrocup5',
    6: 'chrocup6', 7: 'chrocup7', 8: 'chrocup8', 9: 'chrocup9', 10: 'chrocup10',
    11: 'chrocup11', 12: 'chrocup12', 13: 'chrocup13', 14: 'chrocup14', 15: 'chrocup15',
    16: 'chromatic16', 17: 'chrocup17', 18: 'jjk3mst5', 19: 'nk5jnplt', 20: 'chrocup20',
    21: 'chrocup21', 22: 'chromatic22', 23: 'chrocup23', 24: 'nf3a6wpj', 25: 'chrocup25',
    26: 'cwneblan', 27: 'ChromaticCup27', 28: 'kd1khywe', 29: 'ChromaticCup29', 30: 'ChromaticCup30',
    31: 'ChromaticCup31', 32: 'ChromaticCup32', 33: 'ChromaticCup33', 34: 'ChromaticCup34',
    35: 'ChromaticCup35', 36: 'ChromaticCup36', 37: 'ChromaticCup37', 38: 'ChromaticCup38',
    39: 'ChromaticCup39', 40: 'ChromaticCup40', 41: 'ChromaticCup41', 42: 'ChromaticCup42',
    43: 'ChromaticCup43', 44: 'ChromaticCup44', 45: 'ChromaticCup45', 46: 'ChromaticCup46',
    47: 'ChromaticCup47', 48: 'ChromaticCup48', 49: 'ChromaticCup49', 50: 'ChromaticCup50',
    51: 'ChromaticCup51', 52: 'ChromaticCup52', 53: 'ChromaticCup53', 54: 'ChromaticCup54',
    55: 'ChromaticCup55',
}

all_raw_data = {}

for num in sorted(tournament_slugs.keys()):
    slug = tournament_slugs[num]
    url = f"https://challonge.com/{slug}"
    print(f"Fetching CC{num}/{slug}...", end=" ", flush=True)

    try:
        resp = scraper.get(url, timeout=30)
        if resp.status_code != 200:
            print(f"HTTP {resp.status_code}")
            continue

        pattern = r"window\._initialStoreState\['TournamentStore'\]\s*=\s*(\{.+?\});\s*window\._initialStoreState\['ThemeStore'\]"
        match = re.search(pattern, resp.text, re.DOTALL)
        if not match:
            pattern2 = r"window\._initialStoreState\['TournamentStore'\]\s*=\s*(\{.+?\});"
            match = re.search(pattern2, resp.text, re.DOTALL)
            if not match:
                print("no data")
                continue

        data = json.loads(match.group(1))
        tourn = data['tournament']
        matches_by_round = data['matches_by_round']

        raw_players = {}
        for rk, rl in matches_by_round.items():
            for m in rl:
                for side in ['player1', 'player2']:
                    p = m.get(side)
                    if p and p['id'] not in raw_players:
                        raw_players[p['id']] = p['display_name'].strip()

        total_players = len(raw_players)
        tourn_type = tourn.get('tournament_type', 'unknown')

        win_counts = defaultdict(int)
        loss_counts = defaultdict(int)

        for rk, rl in matches_by_round.items():
            for m in rl:
                p1 = m.get('player1')
                p2 = m.get('player2')
                if not p1 or not p2:
                    continue
                pid1, pid2 = p1['id'], p2['id']
                wid = m.get('winner_id')
                if wid:
                    if wid == pid1:
                        win_counts[pid1] += 1
                        loss_counts[pid2] += 1
                    else:
                        win_counts[pid2] += 1
                        loss_counts[pid1] += 1

        # Winner = last match in final (highest positive) round
        winner_id = None
        runner_up_id = None
        pos_rounds = sorted([int(r) for r in matches_by_round.keys() if int(r) > 0], reverse=True)
        if pos_rounds:
            final_round = str(pos_rounds[0])
            final_matches = matches_by_round[final_round]
            last = final_matches[-1]
            if last.get('state') == 'complete' and last.get('winner_id'):
                winner_id = last['winner_id']
                runner_up_id = last.get('loser_id')

        player_last_round = {}
        for r_str, rl in matches_by_round.items():
            r = int(r_str)
            for m in rl:
                if m.get('state') != 'complete':
                    continue
                for s in ['player1', 'player2']:
                    p = m.get(s)
                    if p:
                        player_last_round[p['id']] = r
                lid = m.get('loser_id')
                if lid:
                    player_last_round[lid] = r
                wid = m.get('winner_id')
                if wid:
                    player_last_round[wid] = r

        if winner_id:
            player_last_round[winner_id] = 999

        placements = {}
        if winner_id:
            placements[winner_id] = 1
        if runner_up_id and runner_up_id != winner_id:
            placements[runner_up_id] = 2

        remaining = [pid for pid in raw_players if pid not in placements]
        remaining.sort(key=lambda pid: player_last_round.get(pid, -999), reverse=True)
        for i, pid in enumerate(remaining):
            placements[pid] = 3 + i

        raw_players_str = {str(k): v for k, v in raw_players.items()}
        placements_str = {str(k): v for k, v in placements.items()}
        all_raw_data[str(num)] = {
            'num': num, 'slug': slug, 'type': tourn_type,
            'total_players': total_players,
            'winner_id': str(winner_id) if winner_id else None,
            'runner_up_id': str(runner_up_id) if runner_up_id else None,
            'players': raw_players_str,
            'win_counts': {str(k): v for k, v in win_counts.items()},
            'loss_counts': {str(k): v for k, v in loss_counts.items()},
            'placements': placements_str,
        }

        print(f"OK ({total_players} players)")

    except Exception as e:
        print(f"ERROR: {e}")

    time.sleep(0.3)

with open('tournament_data.json', 'w') as f:
    json.dump(all_raw_data, f, indent=2)

print(f"\nSaved {len(all_raw_data)} tournaments to tournament_data.json")
