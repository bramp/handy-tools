#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Generates a summary of the distribution of the data
# by Andrew Brampton
#

import sys
from collections import defaultdict
from itertools import *
from math import *
from _hist import *

def summary_print(hist):
	keys = sorted(hist.keys())

	largest_count = max(hist.values())

	largest_key  = keys[-1]
	smallest_key = keys[0]

	N = 0; sum = 0; sum2 = 0
	for k in keys:
		count = hist[k]
		weight = k * count

		N += count
		sum  += weight
		sum2 += weight * weight

	mean = sum / N
	variance = (sum2 - (sum*sum) / N) / N

	# We calculate the 90/95/99 percentiles. We use actual values, but perhaps we should interpolate
	c50 = N * 0.5
	c90 = N * 0.90
	c95 = N * 0.95
	c99 = N * 0.99

	p50 = None; p90 = None; p95 = None; p99 = None;

	start = 0
	for k in keys:
		count = hist[k]
		end   = start + count

		if c50 > start and c50 <= end:
			p50 = k
		if c90 > start and c90 <= end:
			p90 = k
		if c95 > start and c95 <= end:
			p95 = k
		if c99 > start and c99 <= end:
			p99 = k

		start += count

	# Print useful stats at the end
	print "# N: {N}, min: {min}, max: {max}, mean: {mean:0.4f}, var: {variance:0.4f}".format(
		N=N, min=smallest_key, max=largest_key, mean=mean, variance=variance)
	print "# median: {median}, 90%: {p90}, 95%: {p95}, 99%: {p99}".format(
		median=p50, p90=p90, p95=p95, p99=p99)


def main(f, bins = 10, min = None, max = None):
	raw = defaultdict(int)
	for line in f:
		try:
			line = line.strip()
			x = float(line)
			raw[x] += 1
		except ValueError:
			print >> sys.stderr, "invalid value '{err}'".format(err=line)
			continue

	if len(raw) > 0:
		hist = hist_ss(raw)
		hist_print(hist)
		summary_print(raw)

#f = open(filename, 'r')
#for line in f:
#    process(line)
#f.close()

if __name__ == "__main__":
	f = sys.stdin
	main(f)
