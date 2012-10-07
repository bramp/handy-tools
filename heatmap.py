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
from _hist import *

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
