---
title: "Minimal Conda Setup Instructions"
subtitle: ""
summary: "Trying to come up with the shortest amount of facts for a successful scientific Python 
environment install while you understand what you are doing. ;)"
author: "Michael Aye"
categories: [python, conda, software management]
date: 2021-10-15T12:36:10-06:00
lastmod: 2026-09-09T00:00:00-06:00
draft: false
---

> **Update 2026:** This post originally told you to install `mamba` alongside `conda`. That
> advice is obsolete. Since conda 23.10 the fast `libmamba` solver is conda's *default*, so
> plain `conda` is now as fast as `mamba` ever was. `Mambaforge` was deprecated in July 2024
> and retired in January 2025; use `Miniforge3` instead. All commands below are plain `conda`.

There's an increasing amount of folks complaining that 
they need to watch a video for all their setting up tools etc.

In this vein, let me summarize what I consider a minimal list of facts and terminal commands to get up and
running with a conda-based scientific Python environment.

## Some basic facts to understand

A few facts that help to understand what's going on below:

* Overall and very approximately (but sufficiently), `conda` is exactly 2 things: 
  * A package/library getter
  * A path manager enabling easy switching between different Python environments.
* The command `conda activate` used below simply creates a temporary PATH variable pointing the system's search
for executables into your currently `activated` conda environment.
* `conda` used to be painfully slow at working out dependencies, which is why a separate tool called `mamba`
existed. That's over: the fast solver was donated to conda itself and has been the default since
conda 23.10, so you do not need any extra tool anymore.
  * If you still have `mamba` installed from the old days, it keeps working, but nothing here requires it.
* conda environments are _ALWAYS_ going into user space, never ever should you require
root/superuser access.
  * Unless you are an admin that installs a systemwide environment for many users.
* conda gets its packages from so called `channels`, and there's a community channel called `conda-forge`
that most of us are using successfully for years.
  * The installer linked below will configure to use the `conda-forge` channel all the time (hence the name
  `miniforge`), but you can always change that later, and, winningly, configure this to be different per
  environment!
  * It is recommended to not install packages from different channels into the same environment
* Creating new environments is fast and cheap (hard-links between downloaded packages when used in more
than one environment.)
  * So, when in doubt if you should install a potentially dodgy Python package into your main work environment,
  maybe better and simply just create a new one (see commands below).


## Installation instructions

### Installing `base`

So, here we go:

1. Download the script-based installer for your operating system here:

For a Unix-like platform like macOS and Linux, execute these commands, they will first downlad the
right installer and then run in:

```
wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh
bash Miniforge3-$(uname)-$(uname -m).sh
```

2. Restart the shell (exit -> open new one)

3. Check that you have the `conda` command available:

```
which conda
```
It should point to your chosen install folder + `/condabin`.

### Installing your main work environment

Now you are good to go to:

4. Create your main work environment.

> I DO NOT recommend to work in the `base` environment, because that's used for managing all envs, so if you
mess up in there, you loose all other envs as well (potentially). This is actually very similar to the old
advice on the Mac to not work with the system Python, because the OS was using it for management tasks.

So, let's say you want to create a Python 3.14 environment as your standard.

> **Which Python version? (checked September 2026)**
>
> **Use 3.14.** The full geospatial stack is built for it and installs cleanly: `gdal`,
> `geopandas`, `rasterio`, `shapely`, `cartopy`, `pyproj`, `rioxarray`, `dask-geopandas`.
> That's what my own daily driver runs on.
>
> **Don't use 3.15 yet.** It isn't released (3.15.0rc2 as I write this, final due
> 1 October 2026), and conda-forge has only rebuilt a small share of packages against it.
> I tested this rather than guessed: I took the 111 packages I had explicitly asked for in
> my 3.14 environment and tried to solve each one against 3.15.0rc2. **46 of them have no
> 3.15 build at all**, including `scipy`, `astropy`, `xarray`, `dask`, `h5py`,
> `scikit-learn`, `scikit-image`, `numba`, `pyarrow`, `jupyterlab` and the entire
> geospatial core. `numpy` is already there, but numpy on its own is not a science
> environment. Revisit 3.15 a few months after it ships.
>
> **Rule of thumb: watch `numba`.** It is reliably the last major piece to be ported to a new
> Python, because it pins hard to both CPython's internals and a specific LLVM build. Here is
> when conda-forge's first `osx-arm64` builds for Python 3.14 actually landed:
>
> | package | first 3.14 build |
> |---|---|
> | numpy | 22 Aug 2025 |
> | scipy, shapely | 30 Aug 2025 |
> | gdal | 1 Sep 2025 |
> | rasterio | 17 Sep 2025 |
> | pyarrow, pytables | 2 Oct 2025 |
> | **numba** | **28 Oct 2025** |
>
> `numba` arrived three weeks *after* Python 3.14.0 itself was released, and 67 days after
> `numpy`. So the shortcut is: **if `numba` installs on the new Python, the rest of your
> stack almost certainly does too.** Use it as your green light.
>
> This isn't academic if you plot large rasters. `datashader` depends on `numba`, and
> `datashader` is what powers `rasterize=True` in HoloViews and hvplot. Without it you lose
> the dynamic re-rasterization that redraws an image at the resolution of your current zoom
> window, which is the whole reason you can pan around a huge scene interactively.

I usually call my main envs by the python version that's installed in there, so in this case:

```
conda create -n py314 python=3.14
```
After that's executed successfully you need to activate it:
```
conda activate py314
```

Let's say we want to install some important basic science packages:

```
conda install pandas scipy astropy jupyterlab nb_conda_kernels
```
> `nb_conda_kernels` is an extremely useful package that helps you to easily switch between conda envs inside
jupyter notebooks

This install command will now churn and come back with a *HUGE* list of packages to install because those 
packages are what your wanted ones are based of.

You should confirm the choices by typing return (or `y`) and then `conda` will download quite fast in parallel
the required packages and make them available to your current env.

### PIP installs

What if the package of your choice isn't available on `conda-forge`? (`conda search <pkg_name>`)

Then you could install it from pypi.org using `pip`.

> Unfortunately, pip installs still in 2021 can mess up your conda envs. :(

Having said that, with a bit of care I manage to mix a lot of PIP installs into my conda envs without any issues.
Here is my strategy:

> NOTE: Activate the conda env where you need the pip things BEFORE you start installing with `pip`!
> It's one of the most frequent problems for Python beginners to have not done that and then have `pip` installed
new packages somewhere where you didn't expect it to be.

* Find out what other packages the pip package depends on and install as many of them as possible via 
`conda`.
* As the last step, if possible, only install your required package via pip, like `pip install nbverbose` for example.
* Don't worry if there's other packages coming in, that part works just like in conda.


Let me repeat above advice again in other words as it's really that important:

* `pip` is "current path dependent".
  * That means, you have to activate the conda env where you want things to end up in, because then the PATH points
  to the right `pip`.
  * Yes, every conda env has its own `pip` command.
  * Alternatively, you can use the full path to the pip command you should be using, but I find that to be 
  quite more scary and less user-friendly for new terminal users,
  which is why I prefer my above advice to simply always activate the env where you want things to install.

Hope this helps someone!

Let me know if you have any questions or suggestions in the linked Twitter thread!

[Comment](https://twitter.com/michaelaye/status/1450561395515396100)
