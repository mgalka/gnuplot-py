#! /usr/bin/env python
# $Id$

# Copyright (C) 1998-2001 Michael Haggerty <mhagger@alum.mit.edu>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.  This program is distributed in
# the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more
# details; it is available at <http://www.fsf.org/copyleft/gpl.html>,
# or by writing to the Free Software Foundation, Inc., 59 Temple Place
# - Suite 330, Boston, MA 02111-1307, USA.

"""Gnuplot -- A pipe-based interface to the gnuplot plotting program.

This is the main module of the Gnuplot package.

Written by "Michael Haggerty", mailto:mhagger@alum.mit.edu.  Inspired
by and partly derived from an earlier version by "Konrad Hinsen",
mailto:hinsen@ibs.ibs.fr.  If you find a problem or have a suggestion,
please "let me know", mailto:mhagger@alum.mit.edu.  Other feedback
would also be appreciated.

The Gnuplot.py home page is at

"Gnuplot.py", http://monsoon.harvard.edu/~mhagger/Gnuplot/Gnuplot.html


For information about how to use this module:

1. Check the README file.

2. Look at the example code in demo.py and try running it by typing
   'python demo.py' or 'python __init__.py'.

3. For more details see the extensive documentation strings
   throughout the python source files, especially this file,
   _Gnuplot.py, PlotItems.py, and gp_unix.py.

4. The docstrings have also been turned into html which can be read
   "here", http://monsoon.harvard.edu/~mhagger/Gnuplot/Gnuplot-doc/.
   However, the formatting is not perfect; when in doubt,
   double-check the docstrings.

You should import this file with 'import Gnuplot', not with 'from
Gnuplot import *', because the module and the main class have the same
name, `Gnuplot'.

To obtain the gnuplot plotting program itself, see "the gnuplot FAQ",
ftp://ftp.gnuplot.vt.edu/pub/gnuplot/faq/index.html.  Obviously you
need to have gnuplot installed if you want to use Gnuplot.py.

The old command-based interface to gnuplot has been separated out into
a separate module, oldplot.py.  If you are still using that interface
you should 'import Gnuplot.oldplot'; otherwise you should stick to the
more flexible object-oriented interface contained here.

Features:

 o  Allows the creation of two or three dimensional plots from
    python.

 o  A gnuplot session is an instance of class 'Gnuplot'.  Multiple
    sessions can be open at once.  For example::

        g1 = Gnuplot.Gnuplot()
        g2 = Gnuplot.Gnuplot()

    Note that due to limitations on those platforms, opening multiple
    simultaneous sessions on Windows or Macintosh may not work
    correctly.  (Feedback?)

 o  The implicitly-generated gnuplot commands can be stored to a file
    instead of executed immediately::

        g = Gnuplot.Gnuplot('commands.txt')

    The 'commands.txt' file can then be run later with gnuplot's
    'load' command.  Beware, however: the plot commands may depend on
    the existence of temporary files, which will probably be deleted
    before you use the command file.

 o  Can pass arbitrary commands to the gnuplot command interpreter::

        g('set pointsize 2')

    (If this is all you want to do, you might consider using the
    lightweight GnuplotProcess class defined in gp.py.)

 o  A Gnuplot object knows how to plot objects of type 'PlotItem'.
    Any PlotItem can have optional 'title' and/or 'with' suboptions.
    Builtin PlotItem types:

    * 'Data(array1)' -- data from a Python list or NumPy array
                        (permits additional option 'cols' )

    * 'File('filename')' -- data from an existing data file (permits
                            additional option 'using' )

    * 'Func('exp(4.0 * sin(x))')' -- functions (passed as a string,
                                     evaluated by gnuplot)

    * 'GridData(m, x, y)' -- data tabulated on a grid of (x,y) values
                             (usually to be plotted in 3-D)

    See the documentation strings for those classes for more details.

 o  PlotItems are implemented as objects that can be assigned to
    variables and plotted repeatedly.  Most of their plot options can
    also be changed with the new 'set_option()' member functions then
    they can be replotted with their new options.

 o  Communication of commands to gnuplot is via a one-way pipe.
    Communication of data from python to gnuplot is via inline data
    (through the command pipe) or via temporary files.  Temp files are
    deleted automatically when their associated 'PlotItem' is deleted.
    The PlotItems in use by a Gnuplot object at any given time are
    stored in an internal list so that they won't be deleted
    prematurely.

 o  Can use 'replot' method to add datasets to an existing plot.

 o  Can make persistent gnuplot windows by using the constructor option
    'persist=1'.  Such windows stay around even after the gnuplot
    program is exited.  Note that only newer version of gnuplot support
    this option.

 o  Can plot either directly to a postscript printer or to a
    postscript file via the 'hardcopy' method.

 o  Grid data for the splot command can be sent to gnuplot in binary
    format, saving time and disk space.

 o  Should work under Unix, Macintosh, and Windows.

Restrictions:

 -  Relies on the Numeric Python extension.  This can be obtained from
    "SourceForge", http://sourceforge.net/projects/numpy/.  If you're
    interested in gnuplot, you would probably also want NumPy anyway.

 -  Only a small fraction of gnuplot functionality is implemented as
    explicit method functions.  However, you can give arbitrary
    commands to gnuplot manually::

        g = Gnuplot.Gnuplot()
        g('set data style linespoints')
        g('set pointsize 5')

 -  There is no provision for missing data points in array data (which
    gnuplot allows via the 'set missing' command).

Bugs:

 -  No attempt is made to check for errors reported by gnuplot.  On
    unix any gnuplot error messages simply appear on stderr.  (I don't
    know what happens under Windows.)

 -  All of these classes perform their resource deallocation when
    '__del__' is called.  Normally this works fine, but there are
    well-known cases when Python's automatic resource deallocation
    fails, which can leave temporary files around.

"""

__version__ = '1.5b1'
__cvs_version__ = '$Revision$'

# Other modules that should be loaded for 'from Gnuplot import *':
__all__ = ['utils', 'funcutils', 'oldplot', ]

from gp import GnuplotOpts, GnuplotProcess, test_persist
from PlotItems import OptionException, DataException, \
     PlotItem, Func, File, Data, GridData
from _Gnuplot import Gnuplot


if __name__ == '__main__':
    import demo
    demo.demo()


