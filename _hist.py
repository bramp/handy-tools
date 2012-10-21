#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Generic functions for creating histograms
# by Andrew Brampton
#

import sys
from collections import defaultdict
from itertools import *
import math

def sum_values(data):
	return reduce(lambda x,y: x + y, data.itervalues(), 0)

def quantiles(data, qs):
	"""Returns a map of quantiles to value for the quantils in qs"""

	N = sum_values(data)
	qs = sorted(set(qs))
	qs = dict( zip(qs, map(lambda x: x * N, qs)) )

	start = 0
	results = dict()
	for k, count in sorted(data.items()):
		end = start + count

		# TODO We could shortcircut this loop (if we sort it and do some logic)
		for q, qN in qs.items():
			if qN >= start and qN <= end:
				results[q] = k
				del qs[q]

		start = end

	assert len(qs) == 0, "quantiles() has unfound quantiles %r" % qs

	return results

def hist_quantiles(data, N=10):
	qs = quantiles(data, [float(x) / N for x in range(0, N + 1)])
	return hist_dict(data, limits=sorted(set(qs.values())))

def hist_fd(data):
	"""Use Freedman-Diaconis' choice"""
	qs = quantiles(data, [0, 0.25, 0.75, 1])
	print qs
	iqr = qs[0.75] - qs[0.25]
	range = qs[1] - qs[0]
	n = sum_values(data)
	return hist_dict(data, N = int(range / (2*iqr / math.pow(n, 1/3))))

def hist_sr(data):
	"""Use Square-root choice"""
	return hist_dict(data, N=int(math.sqrt(len(data))))
	#return hist_dict(data, N=int( math.sqrt( sum_values(data) )))


def hist_ss(data):
	"""Optimal bin sizing using the Shimazaki and Shinomoto algorithm
		Shimazaki and Shinomoto, Neural Comput 19 1503-1527, 2007
	"""

	def bin_mean_var(bins):
		"""returns the mean and biased variance"""

		sum = 0
		sum2 = 0
		for v in bins.values():
			sum  += v
			sum2 += v * v

		N = len(bins)
		return (sum / N, (sum2 - (sum*sum) / N) / N)

	# This is rather brute force, but works
	# We try all the bin sizes in a range and use the best one

	diff = max(data.values()) - min(data.values())

	best_C = float("inf")
	best_bin = None
	for N in xrange(2,15): # Try values between 2 and 30
		width = diff / float(N)

		bins = hist_dict(data, N)
		(mean, var) = bin_mean_var(bins)

		C = (2.0 * mean - var) / (width * width)
		if C < best_C:
			best_C = C
			best_bin = bins

	return best_bin

def hist_dict(data, N = None, limits = None):
	"""Places the data into N bins. We assume the data is a dict of X=>count pairs
	   returns a dict of size N with (upper limit => count)
	"""

	if len(data) == 0:
		return data
		#raise ValueError("data must have atleast one value")

	keys = sorted(data.keys())

	if limits is None:
		if N is None:
			raise ValueError("either N or limit must be set")

		min_ = keys[0]
		max_ = keys[-1]

		diff = max_ - min_
		limits = [min_ + i * diff / N for i in range(1, N + 1)]
	elif N is None:
		N = len(limits)
		if N < 2:
			raise ValueError("limits must have atleast 2 elements")
	else:
		raise ValueError("both N and limit can not be set")

	bins = dict( zip(range(0, N), repeat(0, N)) )

	# Assume keys is sorted
	i = 0
	for k in keys:
		# Skip to the correct bin
		while k > limits[i]:
			i+=1

		bins[ i ] += data[k]

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
