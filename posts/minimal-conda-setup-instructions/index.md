---
title: "Minimal Conda Setup Instructions"
subtitle: ""
summary: "Trying to come up with the shortest amount of facts for a successful scientific Python 
environment install while you understand what you are doing. ;)"
author: "Michael Aye"
categories: [python, conda, mamba, software management]
date: 2021-10-15T12:36:10-06:00
lastmod: 2021-10-15T12:36:10-06:00
draft: false
---
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
* The `conda` command line tool is increasingly being replaced by the faster `mamba` tool.
  * `mamba` is a `drop-in` replacement for `conda`, so for all commands you just replace `conda` with `mamba`.
  * However, `mamba` is still using `conda` underneath, so don't uninstall it, you need both!
  * Only install `mamba` into your `base` environment.
    * That's for people who read this and want to add `mamba` to their system.
  	* New starters should use below's installer that exactly does that.
  * Also, there's a few remaining commands that still run smoother using `conda`, so if `mamba` is
  giving you a hard time, just try the same command parameters using `conda` instead of `mamba`
* conda/mamba environments are _ALWAYS_ going into user space, never ever should you require
root/superuser access.
  * Unless you are an admin that installs a systemwide environment for many users.
* conda gets its packages from so called `channels`, and there's a community channel called `conda-forge`
that most of us are using successfully for years.
  * The installer linked below will configure to use the `conda-forge` channel all the time (hence the name
  `mambaforge`), but you can always change that later, and, winningly, configure this to be different per
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
wget https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-$(uname)-$(uname -m).sh
bash Mambaforge-$(uname)-$(uname -m).sh
```

2. Restart the shell (exit -> open new one)

3. Check that you have the `conda` and `mamba` command available:

```
which conda
which mamba
```
They should both point to your chosen install folder + `/condabin`.

### Installing your main work environment

Now you are good to go to:

4. Create your main work environment.

> I DO NOT recommend to work in the `base` environment, because that's used for managing all envs, so if you
mess up in there, you loose all other envs as well (potentially). This is actually very similar to the old
advice on the Mac to not work with the system Python, because the OS was using it for management tasks.

So, let's say you want to create a Python 3.8 environment as your standard
> 3.9 is also fully supported for science analysis I'd say, just some dev tools don't like it yet.

I usually call my main envs by the python version that's installed in there, so in this case:

```
conda create -n py38 python=3.8
```
After that's executed successfully you need to activate it:
```
conda activate py38
```
and *NOW* we change to use `mamba` because the packages we like to install need to be checked for each other's
dependency requirements which is the time consuming task at which `mamba` excels so much.

Let's say we want to install some important basic science packages:

```
mamba install pandas scipy astropy jupyterlab nb_conda_kernels
```
> `nb_conda_kernels` is an extremely useful package that helps you to easily switch between conda envs inside
jupyter notebooks

This install command will now churn and come back with a *HUGE* list of packages to install because those 
packages are what your wanted ones are based of.

You should confirm the choices by typing return (or `y`) and then `mamba` will download quite fast in parallel
the required packages and make them available to your current env.

### PIP installs

What if the package of your choice isn't available on `conda-forge`? (`mamba search <pkg_name>`)

Then you could install it from pypi.org using `pip`.

> Unfortunately, pip installs still in 2021 can mess up your conda envs. :(

Having said that, with a bit of care I manage to mix a lot of PIP installs into my conda envs without any issues.
Here is my strategy:

> NOTE: Activate the conda env where you need the pip things BEFORE you start installing with `pip`!
> It's one of the most frequent problems for Python beginners to have not done that and then have `pip` installed
new packages somewhere where you didn't expect it to be.

* Find out what other packages the pip package depends on and install as many of them as possible via 
`mamba/conda`.
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

