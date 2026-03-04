---
title: "Cassini UVIS Data Product Enhancement"
summary: "A NASA PDART project to upgrade the existing PDS product for the Cassini UVIS instrument. "
author: ["Michael Aye"]
categories: [cassini uvis, pi]
date: 2026-03-04
image: uvis-aurora.jpg
---
This NASA PDART project upgrades the existing Cassini UVIS data products into a modern, science-ready format.
The PI is Matt Tiscareno at the [SETI Institute](https://www.seti.org/); I serve as external consultant and continue to lead most project activities from FU Berlin.

## Objectives

The limited content and inconvenient format of published Cassini Ultraviolet Imaging Spectrograph (UVIS) data products puts a high burden on end users before scientific investigation can begin.
This project produces upgraded data products in a modern format, adds all required metadata to remove the need for time-consuming geometry calculations, and performs default calibrations for the majority of data products.
This benefits all aspects of UVIS science:

* stellar and solar occultations of Saturn,
* emissions from the Titan atmosphere,
* satellite reflectance,
* ring spectroscopy, and more.

## Approach

We create enhanced UVIS data products by pre-calculating an expanded set of geometry parameters for each detector readout and applying a default calibration that varies with the observational scenario.
The additional metadata is included with the original instrument data in PDS4-compatible FITS files.
Python and IDL tools are provided for data access, analysis, and plotting.

## Current status

The project is in its third year. Current work focuses on:

* FITS metadata definition and automation
* The UVIS User Guide — comprehensive documentation for working with the enhanced data products
* Calibration pipeline refinement and validation
