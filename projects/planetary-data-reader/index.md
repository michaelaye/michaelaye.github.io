---
title: "Planetary Data Reader"
summary: "NASA PDART project to create a unified reader for all PDS data"
author: ["Chase Million", "Michael St. Clair", "Michael Aye"]
categories: [co-i, pds, python]
date: 2021-09-07T23:08:18-06:00
---

I am a Collaborator (Co-I until I left the US) in this exciting project, led by Chase Million of [Million Concepts](https://www.millionconcepts.com/).

# Step 1 proposal text:

## Goals and objectives
This project will create an open source, Python-based tool capable of reading the vast majority of data 
(including tables and images) and metadata formats currently archived by the PDS, as well as some 
formats common in planetary science research workflows but not typically archived in PDS 
(e.g. ISIS cube, JP2, GeoTiff). It will offer users a consistent, easily-understandable interface 
that works the same way for all data formats. For instance, a simple command like `read(filename)` 
will return a Python  object that can immediately be used in research workflows or easily converted 
to other formats using pre-existing tools. 

This tool solves a well-known pain point for planetary data users: simply figuring out how to access 
data, especially data archived under PDS3, which often have inconsistent or bespoke formats. PDS is 
in the process of migrating archives to the stricter PDS4 standard, but the timeline for this migration 
is uncertain, and it is unlikely to be completed before 2025. The tool developed under this project 
provides a stopgap solution and also supplements the migration effort in two important ways. 
First, reading PDS3 data formats is one limit on a swift and efficient data migration, so this tool 
will streamline that effort. Second, because this tool will treat PDS3 and PDS4 data identically 
from the end-user perspective, it will future-proof research workflows from the migration. 

## Approach and methodology
This effort will build on proof-of-concept work already undertaken by this team. The majority of data 
archived under PDS3 (including .DAT and .IMG files) use a bitwise structured format sometimes referred 
to as the “PDS3 format.” It is not dissimilar from the FITS file format, but suffers from a much looser 
definition, leading to difficulties reading these files. The major issues in PDS3 that we have identified 
are (1) inconsistent mapping between specified data types and byte-size / order, (2) complex files 
containing multiple or mixed data types, and (3) file format definitions that are not stored in standard 
locations. We have prototyped solutions to these three issues, and the work plan will involve fully 
developing and testing those solutions. Other issues arise less frequently (e.g. one-off “bad” files, 
unique formats) and will be dealt with case-by-case. 

Several Python tools exist for reading subsets of planetary data. They include pds4_tools, PVL, Plio, 
Python wrappers for GDAL and fitsio, Pysis, and SpiceyPy, astropy. These will be reused when appropriate, 
with input and output syntax / behavior wrapped to provide consistent experience across data types. 

A thorough testing suite will also be developed which, in addition to more targeted approaches, will 
scrape PDS data holdings in a systematic way to verify expected behavior and identify issues requiring 
additional development. 
The resulting tool will be released under a permissive license and made publicly available on the PI’s institutional webspace and the NASA PSD Github. 
It will be made available for easy installation through `pip` and `conda` and also submitted as an affiliate package to the PlanetaryPy project. 

## Scope and relevance
The proposed work will “develop and disseminate software tools that facilitate the use of existing 
datasets or that would enable or enhance future science investigations of interest to the Planetary 
Science Division” and is therefore a Software Tool Development and Validation task per section 1.7 
of the solicitation. The proposed work does not include a “science investigation” or application of t
hese tools except as necessary to validate their performance. It is therefore within scope of and 
appropriate for PDART.

[Link to project](https://github.com/MillionConcepts/pdr)

[PDF link](https://www.hou.usra.edu/meetings/planetdata2021/pdf/7096.pdf)
