#!/usr/bin/env fish
#
# update_homepage.fish — refresh the World Cup 2026 standings from live open
# data and deploy the homepage.
#
# Steps:
#   1. Pull latest group-stage results (keyless openfootball feed) → _groups.md
#   2. Smoke-test render of worldcup.qmd (static, no Jupyter kernel)
#   3. Stage only the World Cup files, skip if nothing changed
#   4. Commit + push to main → GitHub Actions renders and publishes to gh-pages
#
# Usage:  ./scripts/update_homepage.fish     (runs from anywhere)

# --- locate repo root from this script's location, cd into it ----------------
set -l script_dir (dirname (status filename))
cd $script_dir/.. ; or begin
    echo "✗ could not enter repo directory"; exit 1
end

# --- must be on main (the branch the publish action deploys from) ------------
set -l branch (git rev-parse --abbrev-ref HEAD)
if test "$branch" != main
    echo "✗ on branch '$branch', but the site deploys from 'main'. Switch first."
    exit 1
end

# --- 1. refresh data ---------------------------------------------------------
echo "▶ 1/4  Fetching latest results → _groups.md"
python3 scripts/update_worldcup_standings.py ; or begin
    echo "✗ data refresh failed (network? feed down?)"; exit 1
end

# --- 2. smoke-test render ----------------------------------------------------
echo "▶ 2/4  Test render (static — must not need Python)"
quarto render worldcup.qmd ; or begin
    echo "✗ render failed — not pushing"; exit 1
end

# --- 3. stage only the World Cup files ---------------------------------------
echo "▶ 3/4  Staging changes"
git add _groups.md _knockout.md _today.md worldcup.qmd custom.scss \
        scripts/update_worldcup_standings.py scripts/update_homepage.fish

if git diff --cached --quiet
    echo "✓ Standings already current — nothing to deploy."
    exit 0
end

# --- 4. commit + push --------------------------------------------------------
set -l n (grep -oE '[0-9]+ group-stage results' _groups.md | head -1)
test -z "$n"; and set n "standings"
set -l stamp (date '+%Y-%m-%d %H:%M')

echo "▶ 4/4  Commit & push ($n)"
git commit -q -m "Refresh World Cup 2026 standings — $n ($stamp)" ; or begin
    echo "✗ commit failed"; exit 1
end
git push origin main ; or begin
    echo "✗ push failed"; exit 1
end

echo "✓ Pushed. The Quarto publish action will update the live site shortly."
echo "  Watch: https://github.com/michaelaye/michaelaye.github.io/actions"
