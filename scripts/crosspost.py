#!/usr/bin/env python3
"""Announce newly added blog posts on Bluesky and Mastodon.

Normally run from CI (`.github/workflows/crosspost.yml`) on a push to main: it
diffs the pushed range, keeps only *added* `posts/<slug>/index.{qmd,md}` files,
waits until the rendered page is actually live on gh-pages, and then posts a
short announcement to both networks.

By hand:

    python scripts/crosspost.py --slug 2026-08-13_planet-four-uncertainty-api --dry-run

Required secrets (as environment variables):

    BLUESKY_HANDLE            e.g. michaelaye.bsky.social
    BLUESKY_APP_PASSWORD      Settings -> App Passwords (NOT the account password)
    MASTODON_INSTANCE         e.g. https://mastodon.online
    MASTODON_ACCESS_TOKEN     Preferences -> Development -> New application,
                              scope `write:statuses`

Opt out of announcing a single post with `crosspost: false` in its frontmatter.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
import yaml

SITE_URL = "https://michaelaye.github.io"
BLUESKY_PDS = "https://bsky.social"
BLUESKY_LIMIT = 300
MASTODON_LIMIT = 500
POST_RE = re.compile(r"posts/[^/]+/index\.(?:qmd|md)$")
FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def run_git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], capture_output=True, text=True, check=True
    ).stdout


def added_posts(before: str, after: str) -> list[Path]:
    """Post files ADDED in the pushed range — edits never re-announce."""
    # A brand-new branch (or the very first push) reports an all-zero parent.
    if not before or set(before) == {"0"}:
        before = f"{after}~1"
    try:
        diff = run_git("diff", "--diff-filter=A", "--name-only", before, after)
    except subprocess.CalledProcessError as exc:
        print(f"git diff {before}..{after} failed, nothing to announce: {exc.stderr.strip()}")
        return []
    return [Path(line) for line in diff.splitlines() if POST_RE.search(line)]


def frontmatter(path: Path) -> dict:
    match = FRONTMATTER_RE.match(path.read_text(encoding="utf-8"))
    return yaml.safe_load(match.group(1)) if match else {}


def post_url(path: Path) -> str:
    return f"{SITE_URL}/posts/{path.parent.name}/"


def wait_until_live(url: str, timeout: int, interval: int = 30) -> bool:
    """Don't announce a link that 404s — the publish workflow runs in parallel."""
    deadline = time.monotonic() + timeout
    while True:
        try:
            if requests.get(url, timeout=30).status_code == 200:
                return True
        except requests.RequestException:
            pass
        if time.monotonic() >= deadline:
            return False
        print(f"  not live yet, retrying in {interval}s: {url}")
        time.sleep(interval)


def clip(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def plain(text: str) -> str:
    """Neither network renders markdown, so drop the inline markup."""
    text = re.sub(r"[`*_]", "", text)
    return re.sub(r"\s*---\s*", " — ", text).strip()


def compose(meta: dict, url: str, limit: int, hashtags: str = "") -> str:
    """Title, then as much of the blurb as fits, then the bare URL."""
    title = clip(plain(str(meta.get("title", "New post"))), limit // 2)
    tail = f"\n\n{url}" + (f"\n\n{hashtags}" if hashtags else "")
    blurb = plain(str(meta.get("summary") or meta.get("subtitle") or ""))
    room = limit - len(title) - len(tail) - 2
    if blurb and room >= 40:
        return f"{title}\n\n{clip(blurb, room)}{tail}"
    return f"{title}{tail}"


def hashtags_for(meta: dict, keep: int = 5) -> str:
    """Mastodon leans on hashtags for discovery; Bluesky needs facets, so skip there."""
    tags = [re.sub(r"[^0-9A-Za-z]", "", str(c)) for c in meta.get("categories", [])]
    return " ".join(f"#{t}" for t in [t for t in tags if t][:keep])


def link_facets(text: str, url: str) -> list[dict]:
    """Bluesky does not autolink: a link needs UTF-8 *byte* offsets, not char ones."""
    data, target = text.encode("utf-8"), url.encode("utf-8")
    start = data.find(target)
    if start < 0:
        return []
    return [
        {
            "index": {"byteStart": start, "byteEnd": start + len(target)},
            "features": [{"$type": "app.bsky.richtext.facet#link", "uri": url}],
        }
    ]


def post_bluesky(meta: dict, url: str, dry_run: bool) -> None:
    text = compose(meta, url, BLUESKY_LIMIT)
    if dry_run:
        print(f"--- bluesky ({len(text)} chars) ---\n{text}\n")
        return
    session = requests.post(
        f"{BLUESKY_PDS}/xrpc/com.atproto.server.createSession",
        json={
            "identifier": os.environ["BLUESKY_HANDLE"],
            "password": os.environ["BLUESKY_APP_PASSWORD"],
        },
        timeout=30,
    )
    session.raise_for_status()
    session = session.json()
    record = {
        "$type": "app.bsky.feed.post",
        "text": text,
        "createdAt": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "langs": ["en"],
        "facets": link_facets(text, url),
        "embed": {
            "$type": "app.bsky.embed.external",
            "external": {
                "uri": url,
                "title": clip(str(meta.get("title", "")), 200),
                "description": clip(str(meta.get("summary") or meta.get("subtitle") or ""), 300),
            },
        },
    }
    response = requests.post(
        f"{BLUESKY_PDS}/xrpc/com.atproto.repo.createRecord",
        headers={"Authorization": f"Bearer {session['accessJwt']}"},
        json={"repo": session["did"], "collection": "app.bsky.feed.post", "record": record},
        timeout=30,
    )
    response.raise_for_status()
    print(f"  bluesky: {response.json().get('uri', 'posted')}")


def post_mastodon(meta: dict, url: str, slug: str, dry_run: bool) -> None:
    text = compose(meta, url, MASTODON_LIMIT, hashtags_for(meta))
    if dry_run:
        print(f"--- mastodon ({len(text)} chars) ---\n{text}\n")
        return
    instance = os.environ["MASTODON_INSTANCE"].rstrip("/")
    response = requests.post(
        f"{instance}/api/v1/statuses",
        headers={
            "Authorization": f"Bearer {os.environ['MASTODON_ACCESS_TOKEN']}",
            # Replaying the workflow re-uses the key, so Mastodon returns the
            # original status instead of creating a duplicate.
            "Idempotency-Key": f"crosspost-{slug}",
        },
        json={"status": text, "visibility": "public", "language": "en"},
        timeout=30,
    )
    response.raise_for_status()
    print(f"  mastodon: {response.json().get('url', 'posted')}")


def announce(path: Path, args: argparse.Namespace) -> None:
    meta = frontmatter(path)
    slug = path.parent.name
    if meta.get("draft") or meta.get("crosspost") is False:
        print(f"{slug}: opted out (draft/crosspost:false), skipping")
        return
    url = post_url(path)
    print(f"{slug}: announcing {url}")
    if not args.dry_run and not wait_until_live(url, args.wait):
        sys.exit(f"{url} never returned 200 within {args.wait}s — not announcing a dead link")
    post_bluesky(meta, url, args.dry_run)
    post_mastodon(meta, url, slug, args.dry_run)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slug", default=os.getenv("POST_SLUG") or None,
                        help="announce this post instead of diffing git")
    parser.add_argument("--before", default=os.getenv("BEFORE_SHA", ""))
    parser.add_argument("--after", default=os.getenv("AFTER_SHA", "HEAD"))
    parser.add_argument("--wait", type=int, default=900,
                        help="seconds to wait for the page to go live (default: 900)")
    parser.add_argument("--dry-run", action="store_true",
                        default=os.getenv("DRY_RUN", "").lower() == "true",
                        help="print the posts instead of sending them")
    args = parser.parse_args()

    if args.slug:
        candidates = [p for p in (Path("posts") / args.slug / f"index.{e}" for e in ("qmd", "md")) if p.exists()]
        if not candidates:
            sys.exit(f"no posts/{args.slug}/index.qmd or .md found")
    else:
        candidates = added_posts(args.before, args.after)

    if not candidates:
        print("no newly added posts in this push — nothing to announce")
        return
    for path in candidates:
        announce(path, args)


if __name__ == "__main__":
    main()
