#!/usr/local/bin/python
# $Id$

# Simple Gnuplot interface.

# Written by Michael Haggerty <mhagger@blizzard.harvard.edu>
# Derived from earlier version by Konrad Hinsen <hinsen@ibs.ibs.fr>

# New restrictions:

# Can only plot 2-d numeric arrays or python sequences which are
# convertable (via Numeric.asarray) to such.

# Does not try to make persistent windows; instead simply leaves
# gnuplot running for as long as the gnuplot object is in existence.

# Cannot plot to a postscript file with the `plot' method; use
# `hardcopy' instead.

import os, string, tempfile, Numeric


# plotitem represents an item that can be plotted by gnuplot.
class plotitem:
    def __init__(self, **keyw):
	pass

    # return a list of the `plot' command(s) necessary to print out
    # this item:
    def commands(self):
	return []

    # if the plot command requires data to be put on stdin (i.e.,
    # `plot ""'), this method will put that data there.
    def pipein(self, file):
	pass


class plotfunc(plotitem):
    def __init__(self, funcstring):
	self.funcstring = funcstring

    def commands(self):
	return [self.funcstring]


# create a temporary file and write set (which must be a 2-D Numeric
# array) to the file.  Delete the file when self is deleted.
#   self.filename -- the filename of the temp file
#   self.columns -- the number of columns of data in the file
#   self.points -- the number of points (lines) of data in the file
class temparrayfile:
    def __init__(self, set):
	# <set> must be a Numeric array
	assert(len(set.shape) == 2)
	(self.points, self.columns) = set.shape
	assert(self.points > 0)
	assert(self.columns > 0)
	self.filename = tempfile.mktemp()
	file = open(self.filename, 'w')
	for point in set:
	    file.write(string.join(map(repr, point.tolist()), ' ') + '\n')
	file.close()

    def __del__(self):
	os.unlink(self.filename)


# <file> is a temparrayfile
# Keyword arguments recognized:
#   using=<n> -- plot that column against line number
#   using=<tuple> -- plot using a:b:c:d etc.
# Other keyword arguments are passed along to plotitem.
class plotsubfile(plotitem):
    def __init__(self, file, using=None, **keyw):
	self.file = file
	if using is None:
	    self.using = ""
	elif type(using) == type(""):
	    self.using = " using " + using
	elif type(using) == type(()):
	    self.using = " using " + string.join(map(repr, using), ':')
	elif type(using) == type(1):
	    self.using = " using " + `using`
	apply(plotitem.__init__, (self,), keyw)

    def __del__(self):
	pass

    def commands(self):
	return ['"' + self.file.filename + '"' + self.using + ' notitle']


# gnuplot plotting object.  A gnuplot basically represents a running
# gnuplot process, while keeping track of the temporary files
# etc. that have been created for communication with that process.
#
# Members:
#   gnuplot -- a pipe to gnuplot or a file gathering the commands
#   itemlist -- a list of the plotitems that are associated with the
#               current plot.
#   

class gnuplot:
    def __init__(self, filename=None):
	if filename == None:
	    self.gnuplot = os.popen('gnuplot', 'w')
	else:
	    # put gnuplot commands into a file:
	    self.gnuplot = open(filename, 'w')
    	self.itemlist = []

    def __del__(self):
	self('quit')
	self.gnuplot.close()

    # send a string to the gnuplot process, followed by a newline:
    def __call__(self, s):
	self.gnuplot.write(s + "\n")
	self.gnuplot.flush()

    # refresh the plot, using the current plotitems:
    def refresh(self):
	plotcmds = []
	for item in self.itemlist:
	    plotcmds = plotcmds + item.commands()
	self('plot ' + string.join(plotcmds, ', '))
	for item in self.itemlist:
	    item.pipein(self.gnuplot)

    # call the gnuplot `plot' command:
    def plot(self, *data):
	# remove old files:
	self.itemlist = []
	apply(self.replot, data)

    # replot the data, possibly adding new plotitems:
    def replot(self, *data):
    	for item in data:
	    if isinstance(item, plotitem):
		self.itemlist.append(item)
	    elif type(item) is type(""):
		self.itemlist.append(plotfunc(item))
	    else:
		# assume data is an array:
		item = Numeric.asarray(item, Numeric.Float)
		file = temparrayfile(item)
		if file.columns == 1:
		    self.itemlist.append(plotsubfile(file))
		else:
		    for i in range(2, file.columns + 1):
			self.itemlist.append(plotsubfile(file, using=(1,i)))
	self.refresh()

    def xlabel(self, s=None):
	if s==None:
	    self('set ylabel')
	else:
	    self('set xlabel "' + s + '"')

    def ylabel(self, s=None):
	if s==None:
	    self('set ylabel')
	else:
	    self('set ylabel "' + s + '"')

    def hardcopy(self, filename = '| lpr'):
	self('set term postscript enhanced')
	self('set output "' + filename + '"')
	self('replot')
	self('set term x11')
	self('set output')


#
# Demo code
#
if __name__ == '__main__':
    from Numeric import *
    import sys

    g1 = gnuplot()
    # List of (x, y) pairs
    g1.plot([(0.,1),(1.,5),(2.,3),(3.,4)])

    g2 = gnuplot()
    # List of y values, file output
    print "Generating postscript file 'junk.ps'"
    g2.plot([[1], [5], [3], [4]])
    g2.hardcopy('junk.ps')

    # Two plots; each given by a 2d array
    x = arange(10)
    y1 = x**2
    y2 = (10-x)**2
    g3 = gnuplot()
    g3.plot(transpose(array([x, y1])), "x**2", transpose(array([x, y2])))

    sys.stdout.write("Press return to continue...\n")
    sys.stdin.readline()

    del g1, g2, g3

