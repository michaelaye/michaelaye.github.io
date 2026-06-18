---
title: "Planet Four"
subtitle: "Studying Mars with the help of Citizen Science"
author: ["Michael Aye", "Tom Ihro", "Ganna Portyankina", "Candice Hansen", "Meg Schwamb", "Tim Michaels", "Chris Lintott", "et al."]
categories: [mars, citizen science, python]
date: 2026-03-15
image: featured.png
---
The Red Planet is a unique and dynamic world.
Through the power of the Internet and its volunteers, we explore the surface, climate, and history of Mars with the Planet Four projects.

It is difficult if not impossible for computer algorithms to accurately map individual polar seasonal fans,
spot araneiform (‘spider’) erosion, and identify polygonal ridges.
These features visible from orbit are easily spotted by the human eye, and volunteers from around the world have contributed by mapping seasonal fans, polygonal ridges, and araneiforms in Mars Reconnaissance Orbiter imagery.

## The v3.1 catalog

The Planet Four Data Catalog **v3.1** is openly available on Zenodo (CC-BY 4.0). It aggregates the classifications of **40,000+ volunteers** across **64,494 tiles** from **469 HiRISE observations** spanning Mars Years 28–33 (~25 regions of interest):

- **265,389 fans** — directional CO₂-jet deposits whose orientation records the surface wind
- **427,404 blotches** — elliptical deposits with no clear direction

**How to cite:** Aye, K.-M., Schwamb, M. E., Portyankina, G., Hansen, C. J., et al. (2026). *Planet Four Data Catalog* (v3.1) [Data set]. Zenodo. [https://doi.org/10.5281/zenodo.19026723](https://doi.org/10.5281/zenodo.19026723)

## p4tools

The [p4tools](https://michaelaye.github.io/p4tools/) Python library provides easy access to the Planet Four citizen-science catalogs. Install via `pip install p4tools` and load any part of the catalog in a couple of lines — each sub-part is downloaded and cached automatically on first use via [pooch](https://www.fatiando.org/pooch/):

```python
from p4tools import io

fans     = io.get_fan_catalog(version="v3.1")
blotches = io.get_blotch_catalog(version="v3.1")
meta     = io.get_meta_data()      # HiRISE observation metadata
coords   = io.get_tile_coords()    # per-tile coordinates
regions  = io.get_region_names()   # region-of-interest labels
```

Beyond the fan and blotch tables, p4tools now retrieves every sub-part of the catalog — the metadata-merged catalog variants, the observation and EDR-index metadata, and the tile-coordinate tables — each fetched and cached the first time you request it. See the [p4tools documentation](https://michaelaye.github.io/p4tools/) for the full API.

## Current research

Our latest analysis covers 469 HiRISE observations spanning Mars Years 28–33, studying inter- and intra-annual variability of dark regolith deposits at Mars’ south pole ([EGU 2026](https://doi.org/10.5194/egusphere-egu26-20832); [FU Berlin planetary seminar, June 2026](/talks/2026-fub-seminar/)).
Across the seasonal south-polar cap the jet-deposit ground coverage has a median of 4.88% and a mean of 9.32% — a strongly right-skewed distribution that repeats well within individual regions across Mars Years, providing new constraints on seasonal CO₂ jet activity.

## Links

- [Planet Four](https://planetfour.space)
- [v3.1 data catalog on Zenodo](https://doi.org/10.5281/zenodo.19026723)
- [FU Berlin planetary seminar talk (2026)](/talks/2026-fub-seminar/)
- [Zooniverse results](https://www.zooniverse.org/projects/mschwamb/planet-four/about/results)
- [p4tools on PyPI](https://pypi.org/project/p4tools/)
- [p4tools documentation](https://michaelaye.github.io/p4tools/)
- [GitHub organization](https://github.com/planetfour)
- [Introduction video](https://www.youtube.com/watch?v=skrk-6UXuV0)
- [Publications](https://paperpile.com/shared/q73Uo6)
