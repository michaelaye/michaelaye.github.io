---
title: "Cassini UVIS Data Product Enhancement"
summary: "A NASA PDART project to upgrade the existing PDS product for the Cassini UVIS instrument. "
author: ["Michael Aye"]
categories: [cassini uvis, pi]
date: 2021-09-07T23:06:21-06:00
---
I am the PI of this NASA PDART project.
Update: I was the PI of this project until I had to give it up when moving back to Germany.
The new PI will be at the [SETI institute](https://www.seti.org/).

## Objectives 
The limited content and inconvenient format of published Cassini Ultraviolet Imaging Spectrograph (UVIS) data products puts a high burden of remaining work tasks on the end user before a scientific investigation can begin. 
We propose to produce an upgraded data product in a modern format, add all required meta-data to remove the need of time-consuming geometry calculations, and perform a default calibration for the majority of data products. 
This will realize enormous gains and scientific efficiency in working with UVIS data. 
The proposed work will spare researchers beyond the UVIS team countless hours dealing with unnecessary technical issues and allow them to concentrate on scientific analysis.
This work benefits all aspects of study related to UVIS observations: 
* stellar and solar occultations of Saturn,
* emissions from the Titan atmosphere, 
* satellite reflectance, 
* ring spectroscopy, and more.

## Methodology 
We propose to create enhanced UVIS data products, based on the datasets available in the PDS, by pre-calculating an expanded set of geometry parameters for each detector readout and applying a default calibration that varies with the observational scenario. This additional geometrical metadata – required for full scientific investigations – will be included with the original instrument data in a PDS4-compatible data product in the FITS format. Furthermore, we plan to merge the search, data management, analysis, and basic plotting into a common programmatic environment (Python and, to some extent, IDL). Procedures in Python and IDL will be provided to work with this product. We will provide basic data plotting routine and their source codes, based on the new data format.

## Relevance
As requested by the PDART solicitation document, section 1.2, we propose to generate higher-order data products for the UVIS instrument that will be delivered to the PDS, in the new and encouraged PDS4 framework. We also are relevant for section 1.7, as we will develop and deliver software tools and source code for basic visualizations of the new data product, and will store all produced source code at NASA’s PDS Github site.
