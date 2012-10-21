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
import getopt


def main(f, bins = 10, min_ = None, max_ = None):
	raw    = defaultdict(int)
	dates  = defaultdict(int)
	values = defaultdict(int)

	for line in f:
		line = line.strip()
		if len(line) == 0: # Skip empty lines
			continue

		data = line.rsplit(None, 1)
		if len(data) != 2:
			print >> sys.stderr, "line does not contain two values '{err}'".format(err=line)
			continue

		try:
			# TODO Accept simple numeric values
			x = dateutil.parser.parse(data[0], fuzzy=True)

		except ValueError:
			print >> sys.stderr, "invalid x value '{err}'".format(err=data[0])
			continue

		try:
			y = float(data[1])
		except ValueError:
			print >> sys.stderr, "invalid y value '{err}'".format(err=data[1])
			continue

		values [ y ] += 1
		dates  [ x ] += 1
		raw    [ (y, x) ] += 1

	dates_N = 20
	values_N = 20

	if len(raw) > 0:
		# Now bin the dates
		#dates_hist  = hist_dict(dates, N = dates_N)
		#values_hist = hist_dict(values, N = values_N)
		dates_hist  = hist_ss(dates)
		values_hist = hist_ss(values)

		grid_max = 0

		limits = sorted(dates_hist.keys())
		first_filter = lambda x: x[0][0] <= y_max
		other_filter = lambda x: x[0][0] > y_min and x[0][0] <= y_max

		current_filter = first_filter

		# Now filter the raw data into a 2D hist
		hist_2d = dict() # [y][x]
		for y_max, values_count in sorted(values_hist.items()):

			# Find all values within y_min and y_max
			h = defaultdict(int)
			for k,v in filter(current_filter, raw.iteritems()):
				h[ k[1] ] += v
			current_filter = other_filter

			assert sum_values(h) == values_count, "filtered list contains wrong number of values %d vs %d" % (len(h), values_count)

			hist_2d[ y_max ] = d = hist_dict(h, limits = limits)
			if len(h) > 0:
				grid_max = max(grid_max, max(d.values()) * y_max)
			y_min = y_max


		svg = svgwrite.Drawing('test.svg', profile='full')
		#svg.add(dwg.line((0, 0), (100, 0), stroke=svgwrite.rgb(10, 10, 16, '%')))
		#svg.add(dwg.text('Test', insert=(0, 0.2), fill='red'))

		box_width  = 24
		box_height = 14

		quantiles = 9
		colors = sequential.Blues[quantiles].hex_colors

		dx = 100
		x = 0
		y = 0

		# Draw label - TODO CSS class!
		label_style = "text-anchor: end; dominant-baseline: central; font-size: 11px; font-family: sans-serif;"

		y = 0
		for k in sorted(values_hist.keys(), reverse=True):
			x = 0
			svg.add( svg.text( k, insert=(dx - 5, y + box_height / 2), style=label_style ) )
			row = hist_2d[k]
			row_max = max(row.values()) if len(row) > 0 else 1
			for date in sorted(dates_hist.keys()): # for each col
				v = row[ date ]
				#c = (v * (quantiles - 1)) / row_max # max on this row
				c = int( (v * k * (quantiles - 1)) / grid_max) # max on this grid
				#print v, k, v*k, grid_max
				assert c < len(colors), "Invalid color"
				r = svg.rect((x + dx,y), (box_width, box_height), fill = colors[c], stroke = "white")
				r.set_desc( v )
				svg.add( r )

				x += box_width
			y += box_height
			print k, row


		# Draw main grid
		#x = 0
		#for k, counts in sorted(hist_2d.items(), reverse=True): # for each row (in that col)
		#	y = 0
			#max_ = max(counts.values())
			#max_ = 1000

		svg.save()

def usage():
	print "Usage: %s [--(x|y)bins=<n>]" % sys.argv[0]

if __name__ == "__main__":

	try:
		opts, args = getopt.getopt(sys.argv[1:], "h", ["help", "xbins=", "ybins="])
	except getopt.GetoptError, err:
		# print help information and exit:
		raise

	f = sys.stdin
	main(f)
