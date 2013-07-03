#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 
# Generates a summary of the distribution of the data
# by Andrew Brampton
#
import sys
import getopt
import svgwrite

from collections import defaultdict
from itertools import *
from math import *
from brewer2mpl import sequential

#from dateutil.parser import *
import dateutil
import dateutil.parser
import datetime

from _hist import *

def parseDateOrFloat(x):
	try:
		# Try a Date
		return dateutil.parser.parse(x, fuzzy=True)

	except ValueError:
		# Then a try a simple float
		return float(x);



def main(f, bins = 10, min_ = None, max_ = None):
	raw    = defaultdict(int)
	dates  = defaultdict(int)
	values = defaultdict(int)
	firstLine = True
	useDates = False

	for line in f:
		line = line.strip()
		if len(line) == 0: # Skip empty lines
			continue

		data = line.rsplit(None, 1)
		if len(data) != 2:
			print("line does not contain two values '{err}'".format(err=line), file=sys.stderr)
			continue

		try:

			# For the first non-invalid line, we test if it's a date or not
			if firstLine:
				x = parseDateOrFloat(data[0]);
				useDates = isinstance(x, datetime.date);
				firstLine = False;

			if useDates:
				x = dateutil.parser.parse(data[0], fuzzy=True)
			else:
				x = float(data[0])

		except ValueError:
			print("invalid x value '{err}'".format(err=data[0]), file=sys.stderr)
			continue

		try:
			y = float(data[1])
		except ValueError:
			print("invalid y value '{err}'".format(err=data[1]), file=sys.stderr)
			continue

		values [ y ] += 1
		dates  [ x ] += 1
		raw    [ (y, x) ] += 1

	dates_N = 40
	values_N = 20

	if len(raw) > 0:
		# Now bin the dates
		dates_hist  = hist_dict(dates, N = dates_N)

		#values_hist = hist_dict(values, N = values_N)
		values_hist = hist_dict(values, limits = map(lambda x: math.pow(1.3,x-3), range(20)))
		#values_hist = hist_quantiles(values, N = values_N)

		#dates_hist  = hist_ss(dates)
		#values_hist = hist_ss(values)

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
			for k,v in filter(current_filter, raw.items()):
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

		dy = 0
		dx = 50
		x = 0
		y = 0

		# Draw label - TODO CSS class!
		xlabel_style = "text-anchor: end; dominant-baseline: central; font-size: 11px; font-family: sans-serif;"
		ylabel_style = "text-anchor: end; dominant-baseline: central; font-size: 11px; font-family: sans-serif;"

		sorted_dates = sorted(dates_hist.keys())

		for x, date in enumerate(sorted_dates): # for each col
			if useDates:
				date = date.replace(second=0, microsecond=0)
			else:
				date = round_to_sf(date, 3)

			p = (dx + x * box_width + box_width/2, dy + len(values_hist) * box_height)
			svg.add( svg.text( date, insert=p, style=ylabel_style, transform="rotate(-90, %d,%d)" % p ) )

		y = dy
		for k in sorted(values_hist.keys(), reverse=True):
			x = dx
			svg.add( svg.text( round_to_sf(k,3), insert=(x - 5, y + box_height / 2), style=xlabel_style ) )
			row = hist_2d[k]
			row_max = max(row.values()) if len(row) > 0 else 1
			if row_max == 0:
				row_max = 1

			for date in sorted_dates: # for each col
				v = row[ date ]
				#c = int( (v * k * (quantiles - 1)) / grid_max) # max on this grid

				m = list(map(lambda k: hist_2d[k][date], values_hist.keys()))
				col_max = max( m ) if len(m) > 0 else 1
				if col_max == 0:
					col_max = 1

				#c = int( (v * (quantiles - 1)) / row_max) # max on this row
				c = int( (v * (quantiles - 1)) / col_max) # max on this row
				
				assert c < len(colors), "Invalid color"
				r = svg.rect((x,y), (box_width, box_height), fill = colors[c], stroke = "white")
				r.set_desc( v )
				svg.add( r )

				x += box_width
			y += box_height
			print(k, row)


		# Draw main grid
		#x = 0
		#for k, counts in sorted(hist_2d.items(), reverse=True): # for each row (in that col)
		#	y = 0
			#max_ = max(counts.values())
			#max_ = 1000

		svg.save()

def usage():
	print("Usage: %s [--(x|y)bins=<n>]" % sys.argv[0])

if __name__ == "__main__":

	try:
		opts, args = getopt.getopt(sys.argv[1:], "h", ["help", "xbins=", "ybins="])
	except getopt.GetoptError as err:
		# print help information and exit:
		raise

	f = sys.stdin
	main(f)
