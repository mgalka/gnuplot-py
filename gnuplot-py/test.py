#! /usr/bin/env python
# $Id$

"""test.py -- Exercise the Gnuplot.py module.

Copyright (C) 1999-2001 Michael Haggerty <mhagger@alum.mit.edu>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or (at
your option) any later version.  This program is distributed in the
hope that it will be useful, but WITHOUT ANY WARRANTY; without even
the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
PURPOSE.  See the GNU General Public License for more details; it is
available at <http://www.fsf.org/copyleft/gpl.html>, or by writing to
the Free Software Foundation, Inc., 59 Temple Place - Suite 330,
Boston, MA 02111-1307, USA.

This module is not meant to be a flashy demonstration; rather it is a
thorough test of many combinations of Gnuplot.py features.

"""

__cvs_version__ = '$Revision$'

import math, time, tempfile
import Numeric
from Numeric import NewAxis

try:
    import Gnuplot, Gnuplot.PlotItems, Gnuplot.funcutils
except ImportError:
    # kludge in case Gnuplot hasn't been installed as a module yet:
    import __init__
    Gnuplot = __init__
    import PlotItems
    Gnuplot.PlotItems = PlotItems
    import funcutils
    Gnuplot.funcutils = funcutils


def wait(str=None, prompt='Press return to show results...\n'):
    if str is not None:
        print str
    raw_input(prompt)


def main():
    """Exercise the Gnuplot module."""

    wait('Popping up a blank gnuplot window on your screen.')
    g = Gnuplot.Gnuplot()
    g.clear()

    # Make a temporary file:
    filename1 = tempfile.mktemp()
    f = open(filename1, 'w')
    for x in Numeric.arange(100)/5. - 10.:
        f.write('%s %s %s\n' % (x, math.cos(x), math.sin(x)))
    f.close()
    # ensure that file will be deleted upon exit:
    file1 = Gnuplot.PlotItems.TempFile(filename1)

    print '############### test Func ########################################'
    wait('Plot a gnuplot-generated function')
    g.plot(Gnuplot.Func('sin(x)'))

    wait('Set title and axis labels and try replot()')
    g.title('Title')
    g.xlabel('x')
    g.ylabel('y')
    g.replot()

    wait('Style linespoints')
    g.plot(Gnuplot.Func('sin(x)', with='linespoints'))
    wait('title=None')
    g.plot(Gnuplot.Func('sin(x)', title=None))
    wait('title="Sine of x"')
    g.plot(Gnuplot.Func('sin(x)', title='Sine of x'))
    wait('axes=x2y2')
    g.plot(Gnuplot.Func('sin(x)', axes='x2y2', title='Sine of x'))

    print 'Change Func attributes after construction:'
    f = Gnuplot.Func('sin(x)')
    wait('Original')
    g.plot(f)
    wait('Style linespoints')
    f.set_option(with='linespoints')
    g.plot(f)
    wait('title=None')
    f.set_option(title=None)
    g.plot(f)
    wait('title="Sine of x"')
    f.set_option(title='Sine of x')
    g.plot(f)
    wait('axes=x2y2')
    f.set_option(axes='x2y2')
    g.plot(f)

    print '############### test File ########################################'
    wait('Generate a File from a filename')
    g.plot(Gnuplot.File(filename1))
    wait('Generate a File given a TempFile object')
    g.plot(Gnuplot.File(file1))

    wait('Style lines')
    g.plot(Gnuplot.File(filename1, with='lines'))
    wait('using=1, using=(1,)')
    g.plot(Gnuplot.File(filename1, using=1, with='lines'),
           Gnuplot.File(filename1, using=(1,), with='points'))
    wait('using=(1,2), using="1:3"')
    g.plot(Gnuplot.File(filename1, using=(1,2)),
           Gnuplot.File(filename1, using='1:3'))
    wait('title=None')
    g.plot(Gnuplot.File(filename1, title=None))
    wait('title="title"')
    g.plot(Gnuplot.File(filename1, title='title'))

    print 'Change File attributes after construction:'
    f = Gnuplot.File(filename1)
    wait('Original')
    g.plot(f)
    wait('Style linespoints')
    f.set_option(with='linespoints')
    g.plot(f)
    wait('using=(1,3)')
    f.set_option(using=(1,3))
    g.plot(f)
    wait('title=None')
    f.set_option(title=None)
    g.plot(f)

    print '############### test Data ########################################'
    x = Numeric.arange(100)/5. - 10.
    y1 = Numeric.cos(x)
    y2 = Numeric.sin(x)
    d = Numeric.transpose((x,y1,y2))

    wait('Plot Data, specified column-by-column')
    g.plot(Gnuplot.Data(x,y2, inline=0))
    wait('Same thing, inline data')
    g.plot(Gnuplot.Data(x,y2, inline=1))

    wait('Plot Data, specified by an array')
    g.plot(Gnuplot.Data(d, inline=0))
    wait('Same thing, inline data')
    g.plot(Gnuplot.Data(d, inline=1))
    wait('with="lp 4 4"')
    g.plot(Gnuplot.Data(d, with='lp 4 4'))
    wait('cols=0')
    g.plot(Gnuplot.Data(d, cols=0))
    wait('cols=(0,1), cols=(0,2)')
    g.plot(Gnuplot.Data(d, cols=(0,1), inline=0),
           Gnuplot.Data(d, cols=(0,2), inline=0))
    wait('Same thing, inline data')
    g.plot(Gnuplot.Data(d, cols=(0,1), inline=1),
           Gnuplot.Data(d, cols=(0,2), inline=1))
    wait('Change title and replot()')
    g.title('New title')
    g.replot()
    wait('title=None')
    g.plot(Gnuplot.Data(d, title=None))
    wait('title="Cosine of x"')
    g.plot(Gnuplot.Data(d, title='Cosine of x'))

    print '############### test compute_Data ################################'
    x = Numeric.arange(100)/5. - 10.

    wait('Plot Data, computed by Gnuplot.py')
    g.plot(Gnuplot.funcutils.compute_Data(x, lambda x: math.cos(x), inline=0))
    wait('Same thing, inline data')
    g.plot(Gnuplot.funcutils.compute_Data(x, math.cos, inline=1))
    wait('with="lp 4 4"')
    g.plot(Gnuplot.funcutils.compute_Data(x, math.cos, with='lp 4 4'))

    print '############### test hardcopy ####################################'
    print '******** Generating postscript file "gp_test.ps" ********'
    wait()
    g.plot(Gnuplot.Func('cos(0.5*x*x)', with='linespoints 2 2',
                   title='cos(0.5*x^2)'))
    g.hardcopy('gp_test.ps')

    wait('Testing hardcopy options: mode="landscape"')
    g.hardcopy('gp_test.ps', mode='landscape')
    wait('Testing hardcopy options: mode="portrait"')
    g.hardcopy('gp_test.ps', mode='portrait')
    wait('Testing hardcopy options: mode="eps"')
    g.hardcopy('gp_test.ps', mode='eps')
    wait('Testing hardcopy options: eps=1')
    g.hardcopy('gp_test.ps', eps=1)
    wait('Testing hardcopy options: enhanced=1')
    g.hardcopy('gp_test.ps', eps=0, enhanced=1)
    wait('Testing hardcopy options: enhanced=0')
    g.hardcopy('gp_test.ps', enhanced=0)
    wait('Testing hardcopy options: color=1')
    g.hardcopy('gp_test.ps', color=1)
    wait('Testing hardcopy options: solid=1')
    g.hardcopy('gp_test.ps', color=0, solid=1)
    wait('Testing hardcopy options: duplexing="duplex"')
    g.hardcopy('gp_test.ps', solid=0, duplexing='duplex')
    wait('Testing hardcopy options: duplexing="defaultplex"')
    g.hardcopy('gp_test.ps', duplexing='defaultplex')
    wait('Testing hardcopy options: fontname="Times-Italic"')
    g.hardcopy('gp_test.ps', fontname='Times-Italic')
    wait('Testing hardcopy options: fontsize=20')
    g.hardcopy('gp_test.ps', fontsize=20)
    wait('Testing hardcopy options: mode="default"')
    g.hardcopy('gp_test.ps', mode='default')

    print '############### test shortcuts ###################################'
    wait('plot Func and Data using shortcuts')
    g.plot('sin(x)', d)

    print '############### test splot #######################################'
    wait('a 3-d curve')
    g.splot(Gnuplot.Data(d, with='linesp', inline=0))
    wait('Same thing, inline data')
    g.splot(Gnuplot.Data(d, with='linesp', inline=1))

    print '############### test GridData and compute_GridData ###############'
    # set up x and y values at which the function will be tabulated:
    x = Numeric.arange(35)/2.0
    y = Numeric.arange(30)/10.0 - 1.5
    # Make a 2-d array containing a function of x and y.  First create
    # xm and ym which contain the x and y values in a matrix form that
    # can be `broadcast' into a matrix of the appropriate shape:
    xm = x[:,NewAxis]
    ym = y[NewAxis,:]
    m = (Numeric.sin(xm) + 0.1*xm) - ym**2
    wait('a function of two variables from a GridData file')
    g('set parametric')
    g('set data style lines')
    g('set hidden')
    g('set contour base')
    g.xlabel('x')
    g.ylabel('y')
    g.splot(Gnuplot.GridData(m,x,y, binary=0, inline=0))
    wait('Same thing, inline data')
    g.splot(Gnuplot.GridData(m,x,y, binary=0, inline=1))

    wait('The same thing using binary mode')
    g.splot(Gnuplot.GridData(m,x,y, binary=1))

    wait('The same thing using compute_GridData to tabulate function')
    g.splot(Gnuplot.funcutils.compute_GridData(
        x,y, lambda x,y: math.sin(x) + 0.1*x - y**2,
        ))

    wait('Use compute_GridData in ufunc and binary mode')
    g.splot(Gnuplot.funcutils.compute_GridData(
        x,y, lambda x,y: Numeric.sin(x) + 0.1*x - y**2,
        ufunc=1, binary=1,
        ))

    wait('And now rotate it a bit')
    for view in range(35,70,5):
        g('set view 60, %d' % view)
        g.replot()
        time.sleep(1.0)

    wait(prompt='Press return to end the test.\n')


# when executed, just run main():
if __name__ == '__main__':
    main()

