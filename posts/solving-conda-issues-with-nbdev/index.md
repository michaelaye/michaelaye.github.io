---
# Documentation: https://wowchemy.com/docs/managing-content/

title: "Solving Conda Issues With nbdev"
subtitle: ""
summary: "I was never able to create a conda package with nbdev until now, after I dug into the issue. I report on my findings."
authors: []
tags: [python, packaging]
categories: []
date: 2021-10-29T15:21:41-06:00
lastmod: 2021-10-29T15:21:41-06:00
featured: true
draft: true

# Projects (optional).
#   Associate this post with one or more of your projects.
#   Simply enter your project's folder or file name without extension.
#   E.g. `projects = ["internal-project"]` references `content/project/deep-learning/index.md`.
#   Otherwise, set `projects = []`.
projects: []
---
Found several issues:

* Old Makefiles use `nbdev_conda_package` that doesn't exist anymore
  * Instead, the `fastrelease` package is being used
* Even the newer Makefiles with `fastrelease_conda_package` have this issue:
  * When creation of conda package fails, the version is still being bumped
  * This creates a follow-up error the next time you try to create the package because now the meta file creator
  searches for a non-existing version on pypi and the whole process just throws a 404 error without any feedback to 
  the user from where this comes.
* `conda-build` and `boa` need to be installed so that the default `conda mambabuild` can execute
