#!/usr/bin/env python
# Turns a series of numbers into counts per second
# by Andrew Brampton 2009
# TODO Make this smarter, so that it can parse numbers in blocks of text, and highlight the numbers it is changing.
# TODO Make sure the value is divided by the real interval
# TODO If the number printed is smaller than the previous number, then make sure to add extra padding to remove the old number
#
import subprocess
import sys
import time
import datetime
import re
import curses
import getopt

def usage():
	print "%s [--interval=<n>] <command>" % sys.argv[0]

if len(sys.argv) <= 1:
	usage()
	sys.exit(2)

try:
	opts, args = getopt.getopt(sys.argv[1:], "h", ["help", "interval="])
except getopt.GetoptError, err:
	# print help information and exit:
	print str(err) # will print something like "option -a not recognized"
	usage()
	sys.exit(2)

interval = 1.0

for o, a in opts:
	if o in ("-h", "--help"):
		usage()
		sys.exit()
	elif o == "--interval":
		interval = float(a)
	else:
		assert False, "unhandled option"

stdscr = curses.initscr()

# Run the command
try:
	prevNums = []
	while True:
		# Run the command given on the command line
		p1 = subprocess.Popen(args, bufsize=1, stdout=subprocess.PIPE)
		command = p1.communicate()[0].strip();
		lines = command.split('\n')

		now = time.time()
		matches = 0

		stdscr.move(0,0)
		stdscr.clear()

		# Draw the title bar
		stdscr.addstr( "Every %is: %s" % (interval, " ".join(args)) )
		#  with the date/time in the top right corner
		maxY, maxX = stdscr.getmaxyx()
		titleTime = time.strftime("%c", time.gmtime(now))

		stdscr.addstr( 0, maxX - len(titleTime), titleTime + '\n' )

		for line in lines:
			lastEnd = 0

			# Parse the line to find all numbers
			for m in re.finditer( r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?', line):
				num = float( m.group(0) )

				# Print anything before the number and after the last match
				stdscr.addstr( line[lastEnd:m.start():])

				# If we haven't seen a number previous just print the text
				if len(prevNums) <= matches:
					prevNums.append(num)
					stdscr.addstr( line[m.start():m.end()])
				else:
				# Otherwise work out the difference and print it in bold
					diff  = num - prevNums[matches]
					diff /= (now - lastTime)
					prevNums[matches] = num
					if diff == 0:
						stdscr.addstr(line[m.start():m.end()])
					else:
						if diff > 100:
							newNum = ("%i/s" % diff)
						else:
							newNum = ("%.2f/s" % diff)

						stdscr.addstr( newNum, curses.A_BOLD)

				lastEnd = m.end()
				matches += 1

			# Print out the rest of the line (after the last match)
			stdscr.addstr( line[lastEnd:] )

			# Stop us overflowing off the bottom of the screen
			y,x = stdscr.getyx()
			maxY, maxX = stdscr.getmaxyx()

			if y > maxY - 2:
				break

			stdscr.addstr( "\n" )

		stdscr.refresh()
		lastTime = now

		time.sleep( interval )

except KeyboardInterrupt:
	pass
finally:
	curses.endwin()
