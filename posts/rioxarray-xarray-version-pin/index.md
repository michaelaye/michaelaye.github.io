---
title: "Why rioxarray 0.21 Won't Install with xarray 2026"
subtitle: "Tracing a version pin from a slice indexing regression"
summary: "rioxarray 0.21 pins xarray<2025.12 due to a slice normalization bug — but the pin is too broad and blocks fixed 2026 versions too. Here's what happened and how to work around it."
author: "Michael Aye"
categories: [python, geospatial, xarray, rioxarray, debugging]
date: 2026-03-02
featured: true
draft: false
---

If you've recently tried to install `rioxarray` alongside a current `xarray`, you've likely hit something like this:

```
ERROR: Cannot install rioxarray==0.21.0 because these package versions have conflicting dependencies.
    rioxarray 0.21.0 depends on xarray<2025.12,>=2024.7.0
```

Your perfectly fine `xarray 2026.1` is being rejected.
What happened?

## The dependency change

Comparing the two releases on PyPI:

| | rioxarray 0.20.0 (Oct 2025) | rioxarray 0.21.0 (Jan 2026) |
|---|---|---|
| xarray constraint | `>=2024.7.0` | `>=2024.7.0,<2025.12` |

That `<2025.12` upper bound is new, and it's what blocks all of xarray 2026.x.

## The root cause: xarray 2025.12.0

xarray 2025.12.0 shipped [PR #10948](https://github.com/pydata/xarray/pull/10948), which changed how `LazilyIndexedArray` handles slice normalization.
The intent was to fix [#10941](https://github.com/pydata/xarray/issues/10941), but it introduced a regression with negative-step slices ([#11000](https://github.com/pydata/xarray/issues/11000)):

```python
from xarray.core.indexing import normalize_indexer, _decompose_slice

# This now breaks:
_decompose_slice(normalize_indexer(slice(-1, None, -1), 8), 8)
# IndexError: range object index out of range
```

The problem: `slice.indices(8)` on a reverse slice returns `(7, -1, -1)` — a negative stop — which gets misinterpreted as a relative-from-end index rather than an absolute bound.

rioxarray hits this code path in raster operations that involve axis flipping (e.g., north-to-south for certain CRS transforms), so this broke real workflows.

## The pin

The rioxarray maintainer added the pin in [PR #881](https://github.com/corteva/rioxarray/pull/881) (December 2025) to protect users from the broken xarray release.
Reasonable decision at the time — but the constraint `<2025.12` is too broad.
It blocks xarray 2026.1+, which contains the fix ([PR #11044](https://github.com/pydata/xarray/pull/11044)).

The resulting user pain is tracked in [rioxarray #902](https://github.com/corteva/rioxarray/issues/902).

## Workarounds (right now)

**Option 1: Pin xarray to the last pre-regression version**

```bash
pip install "rioxarray==0.21.0" "xarray>=2024.7.0,<2025.12"
```

The last compatible version is xarray 2025.11.x. This is the safe, stable path.

**Option 2: Install rioxarray from the dev branch**

[PR #907](https://github.com/corteva/rioxarray/pull/907) relaxes the pin to `xarray>=2026.2`:

```bash
pip install git+https://github.com/corteva/rioxarray.git
```

Only do this if you're comfortable running unreleased code.

**Option 3: Wait for rioxarray 0.22.0**

The fix is merged and will ship in the next release.

## Timeline

```
2025-11    xarray PR#10948 — fix lazy slice normalization
2025-11    xarray 2025.12.0 released with the "fix"
2025-12    xarray #11000 — regression discovered
2025-12    rioxarray PR#881 — pin xarray<2025.12
2026-01    xarray PR#11044 — actual fix merged
2026-01    rioxarray 0.21.0 released (with the pin)
2026-02    rioxarray #902 — users report 2026.x conflict
2026-??    rioxarray 0.22.0 — pin relaxed to >=2026.2
```

## Takeaway

This is a textbook example of how a well-intentioned upper-bound version pin can outlive its usefulness.
The pin was correct when xarray 2025.12 was the only version with the bug, but it wasn't updated when xarray shipped the fix.
If you maintain a library, consider pinning to specific broken versions (`!=2025.12.0`) rather than open-ended upper bounds (`<2025.12`) — it's more surgical and won't block future fixes.
