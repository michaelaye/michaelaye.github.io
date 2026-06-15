#!/usr/bin/env python3
"""Refresh the World Cup 2026 group page from live, keyless open data.

Data source: openfootball/worldcup.json (public domain, no API key)
  https://raw.githubusercontent.com/openfootball/worldcup.json/master/2026/worldcup.json

This script is NOT part of the Quarto build — it is run on demand:

    python scripts/update_worldcup_standings.py

It fetches the latest group-stage results, computes the standings, and writes a
fully static partial `_groups.md` that `worldcup.qmd` includes. The site itself
needs no Python/Jupyter to render. To publish an update: run this, then commit
and push the changed `_groups.md`.
"""
from __future__ import annotations
import json
import sys
import urllib.request
from datetime import datetime

FEED = ("https://raw.githubusercontent.com/openfootball/"
        "worldcup.json/master/2026/worldcup.json")

# (name, flag, confederation, role)  role in {"host", "seed", None}
GROUPS = [
    ("A", "Mexico", [
        ("Mexico", "🇲🇽", "CONCACAF", "host"),
        ("Czechia", "🇨🇿", "UEFA", None),
        ("South Africa", "🇿🇦", "CAF", None),
        ("South Korea", "🇰🇷", "AFC", None)]),
    ("B", "Canada", [
        ("Canada", "🇨🇦", "CONCACAF", "host"),
        ("Bosnia and Herzegovina", "🇧🇦", "UEFA", None),
        ("Qatar", "🇶🇦", "AFC", None),
        ("Switzerland", "🇨🇭", "UEFA", None)]),
    ("C", None, [
        ("Brazil", "🇧🇷", "CONMEBOL", "seed"),
        ("Haiti", "🇭🇹", "CONCACAF", None),
        ("Morocco", "🇲🇦", "CAF", None),
        ("Scotland", "🏴\U000e0067\U000e0062\U000e0073\U000e0063\U000e0074\U000e007f", "UEFA", None)]),
    ("D", "United States", [
        ("United States", "🇺🇸", "CONCACAF", "host"),
        ("Australia", "🇦🇺", "AFC", None),
        ("Paraguay", "🇵🇾", "CONMEBOL", None),
        ("Türkiye", "🇹🇷", "UEFA", None)]),
    ("E", None, [
        ("Germany", "🇩🇪", "UEFA", "seed"),
        ("Curaçao", "🇨🇼", "CONCACAF", None),
        ("Ecuador", "🇪🇨", "CONMEBOL", None),
        ("Ivory Coast", "🇨🇮", "CAF", None)]),
    ("F", None, [
        ("Netherlands", "🇳🇱", "UEFA", "seed"),
        ("Japan", "🇯🇵", "AFC", None),
        ("Sweden", "🇸🇪", "UEFA", None),
        ("Tunisia", "🇹🇳", "CAF", None)]),
    ("G", None, [
        ("Belgium", "🇧🇪", "UEFA", "seed"),
        ("Egypt", "🇪🇬", "CAF", None),
        ("Iran", "🇮🇷", "AFC", None),
        ("New Zealand", "🇳🇿", "OFC", None)]),
    ("H", None, [
        ("Spain", "🇪🇸", "UEFA", "seed"),
        ("Cape Verde", "🇨🇻", "CAF", None),
        ("Saudi Arabia", "🇸🇦", "AFC", None),
        ("Uruguay", "🇺🇾", "CONMEBOL", None)]),
    ("I", None, [
        ("France", "🇫🇷", "UEFA", "seed"),
        ("Iraq", "🇮🇶", "AFC", None),
        ("Norway", "🇳🇴", "UEFA", None),
        ("Senegal", "🇸🇳", "CAF", None)]),
    ("J", None, [
        ("Argentina", "🇦🇷", "CONMEBOL", "seed"),
        ("Algeria", "🇩🇿", "CAF", None),
        ("Austria", "🇦🇹", "UEFA", None),
        ("Jordan", "🇯🇴", "AFC", None)]),
    ("K", None, [
        ("Portugal", "🇵🇹", "UEFA", "seed"),
        ("Colombia", "🇨🇴", "CONMEBOL", None),
        ("DR Congo", "🇨🇩", "CAF", None),
        ("Uzbekistan", "🇺🇿", "AFC", None)]),
    ("L", None, [
        ("England", "🏴\U000e0067\U000e0062\U000e0065\U000e006e\U000e0067\U000e007f", "UEFA", "seed"),
        ("Croatia", "🇭🇷", "UEFA", None),
        ("Ghana", "🇬🇭", "CAF", None),
        ("Panama", "🇵🇦", "CONCACAF", None)]),
]

CONF_FULL = {
    "UEFA": "Europe", "CONMEBOL": "South America",
    "CONCACAF": "North & Central America", "CAF": "Africa",
    "AFC": "Asia", "OFC": "Oceania",
}

# openfootball feed name -> name used in GROUPS above
NAME_MAP = {
    "Bosnia & Herzegovina": "Bosnia and Herzegovina",
    "Czech Republic": "Czechia",
    "Turkey": "Türkiye",
    "USA": "United States",
}


def fetch_matches():
    """Return ({group_letter: [match, ...]}, played_count) from the feed.

    Each match is a normalized dict: date, time, home, away, ft (or None),
    ground. Names are mapped to the GROUPS display names. Matches are sorted
    chronologically within each group.
    """
    with urllib.request.urlopen(FEED, timeout=20) as r:
        data = json.load(r)
    valid = {n for _, _, teams in GROUPS for n, *_ in teams}
    by_group = {ltr: [] for ltr, _, _ in GROUPS}
    played = 0
    for m in data.get("matches", []):
        grp = str(m.get("group", ""))
        if not grp.startswith("Group"):
            continue
        letter = grp.split()[-1]
        if letter not in by_group:
            continue
        home = NAME_MAP.get(m["team1"], m["team1"])
        away = NAME_MAP.get(m["team2"], m["team2"])
        if home not in valid or away not in valid:
            print(f"  ! skipped unmapped match: {m['team1']} v {m['team2']} ({grp})")
            continue
        ft = m.get("score", {}).get("ft")
        by_group[letter].append({
            "date": m.get("date", ""), "time": m.get("time", ""),
            "home": home, "away": away, "ft": ft, "ground": m.get("ground", "")})
        if ft:
            played += 1
    for ltr in by_group:
        by_group[ltr].sort(key=lambda x: (x["date"], x["time"]))
    return by_group, played


def standings_table(letter, teams, matches):
    flag = {name: fl for name, fl, _, _ in teams}
    tbl = {name: dict(P=0, W=0, D=0, L=0, GF=0, GA=0, Pts=0)
           for name, _, _, _ in teams}
    for mt in matches:
        if not mt["ft"]:
            continue
        a, b, ga, gb = mt["home"], mt["away"], mt["ft"][0], mt["ft"][1]
        for t, gf, gax in ((a, ga, gb), (b, gb, ga)):
            s = tbl[t]; s["P"] += 1; s["GF"] += gf; s["GA"] += gax
        if ga > gb:
            tbl[a]["W"] += 1; tbl[a]["Pts"] += 3; tbl[b]["L"] += 1
        elif gb > ga:
            tbl[b]["W"] += 1; tbl[b]["Pts"] += 3; tbl[a]["L"] += 1
        else:
            tbl[a]["D"] += 1; tbl[b]["D"] += 1
            tbl[a]["Pts"] += 1; tbl[b]["Pts"] += 1
    order = sorted(tbl, key=lambda n: (-tbl[n]["Pts"],
                                       -(tbl[n]["GF"] - tbl[n]["GA"]),
                                       -tbl[n]["GF"], n))
    rows = []
    for i, name in enumerate(order, 1):
        s = tbl[name]; gd = s["GF"] - s["GA"]
        gds = f"+{gd}" if gd > 0 else str(gd)
        cls = "q1" if i <= 2 else ("q3" if i == 3 else "")
        rows.append(
            f'<tr class="{cls}"><td class="pos">{i}</td>'
            f'<td class="st-team"><span class="flag">{flag[name]}</span>'
            f'<span class="st-name">{name}</span></td>'
            f'<td>{s["P"]}</td><td>{s["W"]}</td><td>{s["D"]}</td><td>{s["L"]}</td>'
            f'<td>{s["GF"]}</td><td>{s["GA"]}</td><td class="gd">{gds}</td>'
            f'<td class="pts">{s["Pts"]}</td></tr>')
    return (
        '<div class="standings-wrap">'
        '<div class="standings-cap">Standings &middot; top two advance</div>'
        '<table class="standings"><thead><tr>'
        '<th></th><th class="st-team">Team</th>'
        '<th title="Played">P</th><th title="Won">W</th>'
        '<th title="Drawn">D</th><th title="Lost">L</th>'
        '<th title="Goals for">GF</th><th title="Goals against">GA</th>'
        '<th title="Goal difference">GD</th><th title="Points">Pts</th>'
        '</tr></thead><tbody>' + "".join(rows) + '</tbody></table></div>')


def fixtures_block(matches):
    rows = []
    for mt in matches:
        try:
            d = datetime.strptime(mt["date"], "%Y-%m-%d")
            date_lbl = d.strftime("%b ") + str(d.day)
        except ValueError:
            date_lbl = mt["date"]
        if mt["ft"]:
            score = f'{mt["ft"][0]}&ndash;{mt["ft"][1]}'
            cls, meta = "played", mt["ground"]
        else:
            score = "v"
            cls = "upcoming"
            meta = " &middot; ".join(p for p in (mt["ground"], mt["time"]) if p)
        rows.append(
            f'<li class="fixture {cls}">'
            f'<span class="fx-date">{date_lbl}</span>'
            f'<span class="fx-team fx-home">{mt["home"]}</span>'
            f'<span class="fx-score">{score}</span>'
            f'<span class="fx-team fx-away">{mt["away"]}</span>'
            f'<span class="fx-venue">{meta}</span></li>')
    return (
        '<div class="fixtures">'
        '<div class="fixtures-cap">Fixtures &amp; results</div>'
        '<ul class="fixture-list">' + "".join(rows) + '</ul></div>')


def build(by_group):
    out = ["::::: {.panel-tabset}", ""]
    for letter, host, teams in GROUPS:
        matches = by_group[letter]
        lead = teams[0][0]
        role = f"Host nation &middot; {lead}" if host else f"Top seed &middot; {lead}"
        out += [f"## {letter}", "", ":::: {.group-card}"]
        out.append(
            f'<div class="group-head"><div class="group-letter">{letter}</div>'
            f'<div class="group-meta"><div class="group-kicker">Group {letter}</div>'
            f'<div class="group-lead">{role}</div></div></div>')
        out.append('<ol class="team-list">')
        for name, fl, conf, r in teams:
            chip = ('<span class="chip chip-host">Host</span>' if r == "host"
                    else '<span class="chip chip-seed">Pot 1</span>' if r == "seed"
                    else "")
            out.append(
                f'<li class="team"><span class="flag">{fl}</span>'
                f'<span class="team-name">{name}</span>'
                f'<span class="conf" title="{CONF_FULL[conf]}">{conf}</span>{chip}</li>')
        out.append("</ol>")
        out.append(standings_table(letter, teams, matches))
        out.append(fixtures_block(matches))
        out += ["::::", ""]
    out.append(":::::")
    return "\n".join(out) + "\n"


def main():
    print(f"Fetching {FEED}")
    try:
        by_group, applied = fetch_matches()
    except Exception as e:  # noqa: BLE001
        print(f"ERROR fetching feed: {e}", file=sys.stderr)
        return 1
    here = __file__.rsplit("/scripts/", 1)[0]
    header = ("<!-- GENERATED by scripts/update_worldcup_standings.py — do not edit by hand.\n"
              f"     Source: openfootball/worldcup.json · {applied} group-stage results applied. -->\n\n")
    with open(f"{here}/_groups.md", "w") as f:
        f.write(header + build(by_group))
    print(f"Wrote _groups.md ({applied} results applied). "
          "Now: quarto render worldcup.qmd && git commit && git push")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
