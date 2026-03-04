---
title: "JANUS Camera on the JUICE Mission"
summary: "Radiometric calibration and exposure time tools for Jupiter system observations"
author: ["Michael Aye"]
categories: [jupiter, juice, instrumentation, python]
date: 2026-03-04
image: featured.png
---

JANUS (Jovis, Amorum ac Natorum Undique Scrutator) is the optical camera system on ESA's [JUICE mission](https://www.esa.int/Science_Exploration/Space_Science/Juice) to the Jupiter system. It will image Jupiter's atmosphere, the Galilean moons — particularly Ganymede, Europa, and Callisto — and the broader Jovian environment at visible and near-infrared wavelengths.

My work on JANUS focuses on radiometric calibration, exposure time calculation, and signal-to-noise analysis. I developed the [janus-nbexposure](https://github.com/michaelaye/janus-nbexposure) Python package for computing expected signal levels and optimal exposure times across JANUS observing scenarios, accounting for detector characteristics, optical throughput, and target radiance — including reflected Jupiter-shine on the icy moons.

This work supports observation planning and helps ensure that JANUS achieves its science objectives within the instrument's operational constraints. Funded by the German Federal Ministry of Education and Research (BMBF) through DLR (grant 50QJ2404).

## Links

- [janus-nbexposure](https://github.com/michaelaye/janus-nbexposure) — Exposure calculation package
- [JUICE mission (ESA)](https://www.esa.int/Science_Exploration/Space_Science/Juice)
