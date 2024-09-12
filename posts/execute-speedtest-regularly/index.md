---
title: "Testing your internet speed regularly"
subtitle: "Use crontab and a bit of Python to store speedtest results in a CSV."
summary: ""
author: "Michael Aye"
categories: [hacking, python]
date: 2021-09-21T21:04:05-06:00
draft: false
---
This post is making use of the `speedtest` command line version of Ookla's speedtest tools, which you can get here for various
OSes: https://www.speedtest.net/apps/cli

Specifically, I was looking for a linux solution, and while it's straight forward on the Mac, where the `--csv` flag produces
a CSV string that includes a proper timestamp of the measurement, the interface or API for the `homebrew` CLI versions of Mac and Linux are quite different.

On macOS, one can do

```bash
speedtest --csv
```
 and the output will contain a column with a timestamp which is important
for keeping track of the measurements.

On Linux, however, for getting a CSV output, one needs to do

```bash
speedtest --format=csv
```
and unfortunately here
we do **NOT** get a timestamp in the output.
There is the option to use `--format=json` which actually does provide a timestamp, but I don't want to deal with JSON parsing
for this simple thing.

So I added some bits of Python to catch the output of `speedtest` and add a timestamp to its CSV line before appending it to a
record of measurements.

The `sh` package is a very useful one-file package that enables you to call system programs in a function-like manner, with proper redirection
utilities of any incoming output etc.
BTW, I tried to simply work with the returned object, but it wasn't simply the text, it was some kind of `CommandObject` and the docs are not clear
on how to get the text out of the command object, probably easy but I didn't inspect it.
So maybe below script can be made even easier, without a callback function but directly working with the returned object.

The header line by the way one can get by adding the `--output-header` flag to the above command.
I then just went ahead and added `, time` to the header line, so that the header is complete for a quick pandas import
down the road.

Note that the numbers of `speedtest` are bytes/s, so one does need to do some math to convert to the usual Mbps.

Here's my script:

{{< gist michaelaye 67d3b9668b8667411eb83f77e83def8f  >}}

### Update:
I forgot to add how to run it regularly using `crontab`:

Execute

```bash
crontab -e
```
and an editor should pop up.

The first cryptical looking syntax of crontab, the service that enables you to regularly execute
any program or script on your machine is actually pretty simple, HelpUbuntu has a good intro
here: https://help.ubuntu.com/community/CronHowto

In short, to run a script every hour on the minute 22 you put this into your crontab file:

```bash
22 * * * * /path/to/script/to/run.py
```

Hope it helps someone. 
If anybody wants to see how to quickly analyze and plot the file using `pandas` let me know, but
I figure most of my readers will know that?

Let me know, put any questions or comments you may have on my Twitter feed!
[Comment](https://twitter.com/michaelaye/status/1440729099291402250)
