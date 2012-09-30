A collection of useful command line tools
=========================================

by Andrew Brampton 2009-2012 
<https://github.com/bramp/handy-tools>

persec.py
---------

    ./persec.py [--interval=<n>] <command>

Runs a command at a set interval, and then displays numerical difference between refreshes. For example, `persec.py ifconfig` will display the standard ifconfig, with the bytes and packets numbers displayed in per second values.

<pre><code>
wlan0  Link encap:Ethernet  HWaddr xx:xx:xx:xx:xx:xx
       inet addr:192.168.0.1  Bcast:192.168.0.255  Mask:255.255.255.0
       UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
       RX packets:<strong>539/s</strong> errors:0 dropped:0 overruns:0 frame:0
       TX packets:<strong>517/s</strong> errors:0 dropped:0 overruns:0 carrier:0
       collisions:0 txqueuelen:1000
       RX bytes:<strong>104971/s</strong> (<strong>0.10/s MB</strong>)  TX bytes:<strong>62267/s</strong> (<strong>0.06/s</strong> MB)
</code></pre>


hist.py
-------

    cat something | ./hist.py

Reads a sequence of numbers from stdin, and produces a pretty histogram as well as various statistics such as the mean, median, 95 percentile.

<pre><code>
  <=                               distibution                                count
1.92 ************************************************************************ 20
2.17 ******************                                                        5
2.42 **************                                                            4
2.67 ***                                                                       1
2.92                                                                           0
3.17 **********                                                                3
3.43 *******                                                                   2
3.68 ********************************                                          9
3.93 **************************************************                       14
4.18 ****************************************************************         18
4.43 *******************************************                              12
4.68 ******************************************************                   15
4.93 **************                                                            4
# N: 107, min: 1.67, max: 4.93, mean: 3.4557, var: 12.6348
# median: 3.8, 90%: 4.6, 95%: 4.63, 99%: 4.83
</code></pre>
