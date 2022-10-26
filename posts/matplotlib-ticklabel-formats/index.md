---
# Documentation: https://wowchemy.com/docs/managing-content/

title: "Matplotlib Ticklabel Formats"
subtitle: ""
summary: ""
authors: [michael-aye]
tags: []
categories: [plotting, matplotlib]
date: 2013-09-03
lastmod: 2013-09-03
featured: false
draft: false

# Projects (optional).
#   Associate this post with one or more of your projects.
#   Simply enter your project's folder or file name without extension.
#   E.g. `projects = ["internal-project"]` references `content/project/deep-learning/index.md`.
#   Otherwise, set `projects = []`.
projects: []
---
If you are a heavy matplotlib user, you are bound to have seen the funny offset numbers in the top left of the plot window:  
  

[![](http://2.bp.blogspot.com/-JWVf7z8w_Yc/UiZhRFt-7qI/AAAAAAAAIQk/uGIXoX-LtKM/s320/Screen+Shot+2013-09-03+at+15.22.05+.png)](http://2.bp.blogspot.com/-JWVf7z8w_Yc/UiZhRFt-7qI/AAAAAAAAIQk/uGIXoX-LtKM/s1600/Screen+Shot+2013-09-03+at+15.22.05+.png)

They are obviously there to help the viewer focus on the level where the numbers are really changing, removing the area where there's no change happening.  
  
But I am claiming that due to pattern recognition, there are quite a few cases where this confuses more than it helps. In this example I (and the people in my team) are used to see 5-digit numbers and it takes quite some time to figure out here, that these are indeed 5-digit numbers.  
  
Therefore I researched how to switch this behavior off.  
  
  
First, one imports the ScalarFormatter class from the matplotlib.ticker module:  

  

> from matplotlib.ticker import ScalarFormatter

Then, one creates a formatter object with the use of offset numbers switched off:  
  

> y\_formatter = ScalarFormatter(useOffset=False)

  
Finally, you apply it to an axis object that you either receive via the fig.subplot() command, via plt.gca() (acronym for Get Current Axis) or you catch it when it is being returned after a plot command:  
  

> ax.yaxis.set\_major\_formatter(y\_formatter)

There you go, hope this helps someone.  
  
[Here](http://stackoverflow.com/questions/3677368/matplotlib-format-axis-offset-values-to-whole-numbers-or-specific-number) is the stackoverflow issue that helped me to find the solution.  
  
Update (2013-10-20) :  
  
An easier way is to catch the axis object from the plot command and apply the following command:  

> ax.ticklabel\_format(useOffset=False)

I [initiated](http://stackoverflow.com/questions/18704308/useoffset-false-in-config-file) a [github issue](https://github.com/matplotlib/matplotlib/issues/2400) to have this included in matplotlib, which has been responded already with a solution, so this will be configurable in the future, yay!  
  
Update 2, same day:  
Weird, I thought I had the above shortcut working at some time, now it doesn't. If anyone knows the circumstance under this can work and can not, please comment.
