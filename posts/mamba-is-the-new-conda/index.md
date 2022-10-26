---
title: "Mamba is the new Conda"
subtitle: ""
summary: "Mamba is a drop-in replacement for conda and you should be using it."
author: "Michael Aye"
categories: [conda, mamba, software management]
date: 2021-09-10T13:15:10-06:00
featured: true
draft: false
---
[Mamba](https://mamba.readthedocs.io/en/latest/user_guide/mamba.html) is a CLI tool to manage conda environments and a drop-in replacement for the `conda` CLI tool.
It is built in C/C++ and hence resolves package dependencies much faster than the Python-coded `conda`.

It also offers parallel downloads for new or updated packages, so that updating your environment or adding a new package isn't a chore anymore, it's blazing fast! :)

You install it (only!) into your `conda` `base` environment like so:

```bash
conda activate base
conda install -c conda-forge mamba
```

When creating a new Python system, I can recommend to go immediately for the new [`mambaforge`](https://github.com/conda-forge/miniforge) installer, that will:

* install mamba into your base so that it is immediately available
* point all your package requests to the awesome `conda-forge` channel where a huge community provides all the scientific Python packages and dependencies (like `gdal` and `OpenCV`) in a much faster update cadence then the `defaults` channel of anaconda does.

I am working exclusively with the the `conda-forge` channel for several years and never, or very rarely, had an issue with that.

> Just remember: Don't mix channels much, the less the better. (It's okay for a one-time mamba install into your `base` though.)

[Comment](https://twitter.com/michaelaye/status/1436414613004988418?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E1436414613004988418%7Ctwgr%5E%7Ctwcon%5Es1_c10&ref_url=https%3A%2F%2Fpublish.twitter.com%2F%3Fquery%3Dhttps3A2F2Ftwitter.com2Fmichaelaye2Fstatus2F1436414613004988418widget%3DTweet)

{{< tweet 1436414613004988418 >}}
