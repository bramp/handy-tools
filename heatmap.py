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
import dateutil.parser
import dateutil
import svgwrite
from brewer2mpl import sequential
from bisect import bisect_left

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
	for N in xrange(2,15): # Try values between 2 and 30
		width = diff / float(N)

		bins = hist_dict(data, N)
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


def main(f, bins = 10, min_ = None, max_ = None):
	raw    = defaultdict(int)
	dates  = defaultdict(int)
	values = defaultdict(int)

	for line in f:
		line = line.strip()
		if len(line) == 0:
			continue

		data = line.rsplit(None, 1)
		if len(data) != 2:
			print >> sys.stderr, "invalid line '{err}'".format(err=line)
			continue

		try:
			date = dateutil.parser.parse(data[0])
			#print date

		except ValueError:
			print >> sys.stderr, "invalid date '{err}'".format(err=data[0])
			continue

			#print
		try:
			x = float(data[1])
		except ValueError:
			print >> sys.stderr, "invalid value '{err}'".format(err=data[1])
			continue

		values [ x ] += 1
		dates  [ date ] += 1
		raw    [ (date, x) ] += 1

	dates_N = 20
	values_N = 10

	if len(raw) > 0:
		# Now bin the dates
		#dates_hist  = hist_dict(dates, N = dates_N)
		#values_hist = hist_dict(values, N = values_N)
		dates_hist  = hist_ss(dates)
		values_hist = hist_ss(values)

		limits = sorted(values_hist.keys())

		first_filter = lambda x: x[0][0] <= max_
		other_filter = lambda x: x[0][0] > min_ and x[0][0] <= max_
		current_filter = first_filter

		hist_2d = dict()
		for max_, dates_count in sorted(dates_hist.items()):

			h = defaultdict(int)
			for k,v in filter(current_filter, raw.iteritems()):
				h[ k[1] ] += v
			current_filter = other_filter

#			if first:
#				h = defaultdict()
#				#h = dict((k[1],v) for k,v in filter(lambda k, v: k[0] <= max_, raw.iteritems())# if k[0] <= max_)
#				for k,v in raw.iteritems():
#					if k[0] <= max_: h[k[1]] += v	
#				first = False
#			else:
#				#h = dict((k[1],v) for k,v in raw.iteritems() if k[0] > min_ and k[0] <= max_)
#				h = defaultdict()
#				for k,v in raw.iteritems():
#					if k[0] > min_ and k[0] <= max_: h[k[1]] += v	

			new_dates_count = reduce(lambda x,y: x + y, h.itervalues())
			assert new_dates_count == dates_count, "filtered list contains wrong number of values %d vs %d" % (len(h), dates_count)

			hist_2d[ max_ ] = hist_dict(h, limits = limits)
			min_ = max_


		svg = svgwrite.Drawing('test.svg', profile='full')
		#svg.add(dwg.line((0, 0), (100, 0), stroke=svgwrite.rgb(10, 10, 16, '%')))
		#svg.add(dwg.text('Test', insert=(0, 0.2), fill='red'))

		box_width  = 24
		box_height = 14

		colors = sequential.Blues[9].hex_colors

		dx = 100
		x = 0
		y = 0

		# Draw label
		label_style = "text-anchor: end; dominant-baseline: central; font-size: 11px; font-family: sans-serif;"

		for k in values_hist.keys():
			y += box_height
			svg.add( svg.text( k, insert=(dx - 5, y - box_height / 2), style=label_style ) )

		# Draw main grid
		x = 0
		for date, counts in sorted(hist_2d.items()):
			y = 0
			for k, v in sorted(counts.items(), reverse=True):
				#c = bisect_left(limits, k)
				c = (v * 9) / 1000
				r = svg.rect((x + dx,y), (box_width, box_height), fill = colors[c], stroke = "white")
				r.set_desc( v )
				svg.add( r )

				y += box_height
			x += box_width

			print date, counts

		svg.save()

#		hist = hist_ss(raw)
#		hist_print(hist)
#		summary_print(raw)

#f = open(filename, 'r')
#for line in f:
#    process(line)
#f.close()

if __name__ == "__main__":
	f = sys.stdin
	main(f)
