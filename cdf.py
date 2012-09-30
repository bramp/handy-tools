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

def hist_fd(data):
	"""TODO Use Freedman-Diaconis' choice"""
	pass

def hist_ss(data):
	"""Optimal bin sizing using the Shimazaki and Shinomoto algorithm
		Shimazaki and Shinomoto, Neural Comput 19 1503-1527, 2007
	"""

	# This is rather brute force, but works
	# We try all the bin sizes in a range and use the best one

	diff = max(data.values()) - min(data.values())

	best_C = float("inf")
	best_bin = None
	for N in xrange(2,30):
		width = diff / float(N)

		bins = bin_dict(data, N)
		(mean, var) = bin_mean_var(bins)

		C = (2.0 * mean - var) / (width * width)
		if C < best_C:
			best_C = C
			best_bin = bins

	return best_bin


def bin_mean_var(bins):
	"""returns the mean and biased variance"""

	sum = 0
	sum2 = 0
	for v in bins.values():
		sum  += v
		sum2 += v * v

	N = len(bins)
	return (sum / N, (sum2 - (sum*sum) / N) / N)

def bin_dict(data, N):
	"""Places the data into N bins. We assume the data is a dict of X=>count pairs
	   returns a dict of size N with (upper limit => count)
	"""

	keys = sorted(data.keys())
	min  = keys[0]
	max  = keys[-1]
	diff = max - min

	limits = [min + i * diff / N for i in range(1, N + 1)]

	bins = dict( zip(range(0, N), repeat(0, N)) )

	i = 0
	for k in keys:
		# Skip to the correct bin
		while k > limits[i]:
			i+=1

		bins[ i ] += data[k]
#		bins[ floor( (k - min) / diff * (N-1) )] += data[k]

	return dict( zip ( limits, bins.itervalues() ) )

def hist_print(hist, weight = False, logarithmic = False, width = 80):
	"""Prints a ASCII histogram"""

	keys = sorted(hist.keys())

	largest_count = max(hist.values())

	largest_key  = keys[-1]
	smallest_key = keys[0]

	key_width   = len("{:.2f}".format(largest_key))
	count_width = len("{:d}".format(largest_count))
	stars_width = width - key_width - count_width - 2

	largest_count = float(largest_count) # cast to ensure correct math

	# If using weight, the histogram is drawn based on key * count
	if weight:
		largest_count = 0
		for k, v in hist.items():
			largest_count = max(largest_count, k * v)

	if logarithmic:
		largest_count = log(largest_count)

	print "<=".rjust(key_width) + " " + "distibution".center(stars_width) +  " " + "count".center(count_width)

	n = 0
	for k in keys:
		count = hist[k]

		# Weight the value
		if weight:
			count = count * k

		# Scale it (logarithmically)
		if logarithmic and count > 0:
			count = log(count)

		stars = '*' * int( (count / largest_count) * stars_width )

		print "{key:>{key_width}.2f} {stars:<{stars_width}s} {count:{count_width}d}".format(
			key=k, key_width=key_width,
			stars=stars, stars_width = stars_width,
			count=hist[k], count_width = count_width )

		n += hist[k]

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
			x = float(line.strip())
			raw[x] += 1
		except ValueError:
			continue

	hist = hist_ss(raw)
	hist_print(hist)
	summary_print(raw)

#	for i in range(bins):
#		bin_min = min + i * diff / bins
#		bin_max = min + (i+1) * diff / bins
#		print bin_min, bin_max
#
#	print min, max

#f = open(filename, 'r')
#for line in f:
#    process(line)
#f.close()

if __name__ == "__main__":
	f = sys.stdin
	main(f)
