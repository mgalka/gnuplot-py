#!/usr/local/bin/python -t
# $Id$

"""Gnuplot.py -- A pipe-based interface to the gnuplot plotting program.

Copyright (C) 1998,1999 Michael Haggerty

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

Written by Michael Haggerty <mhagger@blizzard.harvard.edu>.  Inspired
by and partly derived from an earlier version by Konrad Hinsen
<hinsen@ibs.ibs.fr>.  If you find a problem or have a suggestion,
please let me know at <mhagger@blizzard.harvard.edu>.  Other feedback
is also welcome.

For information about how to use this module, see the comments below,
the documentation string for class Gnuplot, and the test code at the
bottom of the file.  You can run the test code by typing
'python Gnuplot.py'.

You should import this file with 'import Gnuplot', not with
'from Gnuplot import *'; otherwise you will have problems with
conflicting names (specifically, the Gnuplot module name conflicts
with the Gnuplot class name).

To obtain the gnuplot plotting program itself, see
<http://www.cs.dartmouth.edu/gnuplot_info.html>.  Obviously you need
to have gnuplot installed if you want to use Gnuplot.py.

Features:

 o  Allows the creation of two or three dimensional plots from
    python by piping commands to the 'gnuplot' program.
 o  A gnuplot session is an instance of class 'Gnuplot'.  Multiple
    sessions can be open at once:
        g1 = Gnuplot.Gnuplot(); g2 = Gnuplot.Gnuplot()
 o  The implicitly-generated gnuplot commands can be stored to a file
    instead of executed immediately:
        g = Gnuplot.Gnuplot('commands.gnuplot')
    The file can then be run later with gnuplot's 'load' command.
    Beware, however: if the plot commands depend on the existence of
    temporary files, they will probably be deleted before you use the
    command file.
 o  Can pass arbitrary commands to the gnuplot command interpreter:
        g('set pointsize 2')
 o  A Gnuplot object knows how to plot objects of type 'PlotItem'.
    Any PlotItem can have optional `title' and/or 'with' suboptions.
    Builtin PlotItem types:
        
    * "Data(array1)" -- data from a Python list or NumPy array
                        (permits additional option 'cols' )
    * "File('filename')" -- data from an existing data file (permits
                            additional option 'using' )
    * "Func('exp(4.0 * sin(x))')" -- functions (passed as a string
                                     for gnuplot to evaluate)
    * "GridData(m, x, y)" -- data tabulated on a grid of (x,y) values
                             (usually to be plotted in 3-D)

    See the documentation strings for those classes for more details.

 o  PlotItems are implemented as objects that can be assigned to
    variables (including their options) and plotted repeatedly ---
    this also saves much of the overhead of plotting the same data
    multiple times.
 o  Communication of data between python and gnuplot is via temporary
    files, which are deleted automatically when their associated
    'PlotItem' is deleted.  (Communication of commands is via a pipe.)
    The PlotItems in use by a Gnuplot object at any given time are
    stored in an internal list so that they won't be deleted
    prematurely.
 o  Can use 'replot' method to add datasets to an existing plot.
 o  Can make persistent gnuplot windows by using the constructor option
    `persist=1'.  Such windows stay around even after the gnuplot
    program is exited.  Note that only newer version of gnuplot support
    this option.
 o  Can plot either to a postscript printer or to a file via
    'hardcopy' method.
 o  There is a 'plot' command which is roughly compatible with the
    command from Konrad Hinsen's old 'Gnuplot.py'.
 o  Grid data for the splot command can be sent to gnuplot in binary
    format, saving time and disk space.

Restrictions:
    
 -  Relies on the Numeric Python extension.  This can be obtained
    from LLNL (See ftp://ftp-icf.llnl.gov/pub/python/README.html).
    If you're interested in gnuplot, you would probably also want
    NumPy anyway.
 -  Probably depends on a unix-type environment.  Anyone who wants
    to help get this running on other platforms should contact me.
 -  Only a small fraction of gnuplot functionality is implemented as
    explicit method functions.  However, you can give arbitrary
    commands to gnuplot manually; for example:
        'g = Gnuplot.Gnuplot()',
        'g('set data style linespoints')',
        'g('set pointsize 5')',
    etc.  I might add a more organized way of setting arbitrary
    options.
 -  There is no provision for missing data points in array data
    (which gnuplot would allow by specifying '?' as a data point).
    I can't think of a clean way to implement this; maybe one could
    use NaN for machines that support IEEE floating point.

Bugs:

 -  No attempt is made to check for errors reported by gnuplot (but
    they will appear on stderr).
 -  All of these classes perform their resource deallocation when
    '__del__' is called.  If you delete things explicitly, there will
    be no problem.  If you don't, an attempt is made to delete
    remaining objects when the interpreter is exited, but this is
    not completely reliable, so sometimes temporary files will be
    left around.  If anybody knows how to fix this problem, please
    let me know.
"""

__version__ = '1.1a'
__cvs_version__ = 'CVS version $Revision$'

import sys

# ############ Configuration variables (optional): #####################

# Command to start up the gnuplot program.  If your version of gnuplot
# is run otherwise, specify the correct command here.  You could also
# append command-line options here if you wish.
if sys.platform == 'win32':
    _gnuplot_command = 'pgnuplot.exe'
else:
    _gnuplot_command = 'gnuplot'

# Recent versions of gnuplot (at least for Xwindows) allow a
# `-persist' command-line option when starting up gnuplot.  When this
# option is specified, graph windows remain on the screen even after
# you quit gnuplot (type `q' in the window to close it).  This can be
# handy but unfortunately it is not supported by older versions of
# gnuplot.  The following configuration variable specifies whether the
# user's version of gnuplot recognizes this option or not.  You can
# set this variable to 1 (supports -persist) or 0 (doesn't support)
# yourself; if you leave it with the value None then the first time
# you create a Gnuplot object it will try to detect automatically
# whether your version accepts this option.
if sys.platform == 'win32':
    # wgnuplot doesn't accept this option, so don't bother testing for it:
    _recognizes_persist = 0
else:
    _recognizes_persist = None

# Recent versions of gnuplot allow you to specify a `binary' option to
# the splot command for grid data, which means that the data file is
# to be read in binary format.  This option saves substantial time
# writing and reading the file, and can also save substantial disk
# space and therefore it is the default for that type of plot.  But if
# you have an older version of gnuplot (or you prefer text format) you
# can disable the binary option in either of two ways: (a) set the
# following variable to 0; (b) pass `binary=0' to the GridData
# constructor.  (Note that the demo uses binary=0 to maximize
# portability.)
_recognizes_binary_splot = 1

# After a hardcopy is produced, we have to set the terminal type back
# to `on screen'.  If you are using unix, then `x11' is probably
# correct.  If not, change the following line to the terminal type you
# prefer to use for on-screen work.
if sys.platform == 'win32':
    _default_term = 'windows'
else:
    _default_term = 'x11'

# Gnuplot can plot to a printer by using "set output '| ...'" where
# ... is the name of a program that sends its stdin to a printer.  On
# my machine the appropriate program is `lpr', as set below.  On your
# computer it may be something different (like `lp'); you can set that
# by changing the variable below.  You can also use the following
# variable to add options to the print command.
_default_lpr = '| lpr'

# ############ End of configuration options ############################

import os, string, tempfile, Numeric

if sys.platform == 'win32':
    from win32pipe import popen
else:
    from os import popen


# _unset is used as a default for unset keyword options
class _unset:
    pass


def test_persist():
    """Determine whether gnuplot recognizes the option '-persist'.

    If the configuration variable _recognizes_persist is set (i.e., to
    something other than None), return that value.  Otherwise, try to
    determine whether the installed version of gnuplot recognizes the
    -persist option.  (If it doesn't, it should emit an error message
    with '-persist' in the first line.)  Then set _recognizes_persist
    accordingly for future reference.

    """

    global _recognizes_persist
    if _recognizes_persist is None:
        g = popen('echo | %s -persist 2>&1' % _gnuplot_command, 'r')
        response = g.readlines()
        g.close()
        _recognizes_persist = ((not response)
                               or (string.find(response[0], '-persist') == -1))
    return _recognizes_persist


def float_array(m):
    """Return the argument as a Numeric array of type at least Float32.

    Leave Float64 unchanged, but upcast all other types to Float32.
    Allow also for the possibility that the argument is a python
    native type that can be converted to a Numeric array using
    Numeric.asarray(), but in that case don't worry about downcasting
    to single-precision float.

    """

    try:
        # Try Float32 (this will refuse to downcast)
        return Numeric.asarray(m, Numeric.Float32)
    except TypeError:
        # That failed for some reason; try to convert to the largest
        # floating-point type:
        return Numeric.asarray(m, Numeric.Float)


def write_array(f, set,
                item_sep=' ',
                nest_prefix='', nest_suffix='\n', nest_sep=''):
    """Write an array of arbitrary dimension to a file.

    A general recursive array writer.  The last four parameters allow
    a great deal of freedom in choosing the output format of the
    array.  The defaults for those parameters give output that is
    gnuplot-readable.  But using, for example, ( ',', '{', '}', ',\n'
    ) would output an array in a format that Mathematica could read.
    item_sep should not contain '%' (or if it does, it should be
    escaped to '%%') since it is put into a format string.

    For 2-d, the default file organization is for example:

        set[0,0] set[0,1] ...
        set[1,0] set[1,1] ...

    etc.  For 3-d, it is for example:

        set[0,0,0] set[0,0,1] ...
        set[0,1,0] set[0,1,1] ...

        set[1,0,0] set[1,0,1] ...
        set[1,1,0] set[1,1,1] ...

    etc.

    """

    if len(set.shape) == 1:
        (columns,) = set.shape
        assert columns > 0
        fmt = string.join(['%s'] * columns, item_sep)
        f.write(nest_prefix)
        f.write(fmt % tuple(set.tolist()))
        f.write(nest_suffix)
    elif len(set.shape) == 2:
        # This case could be done with recursion, but `unroll' for
        # efficiency.
        (points, columns) = set.shape
        assert points > 0 and columns > 0
        fmt = string.join(['%s'] * columns, item_sep)
        f.write(nest_prefix + nest_prefix)
        f.write(fmt % tuple(set[0].tolist()))
        f.write(nest_suffix)
        for point in set[1:]:
            f.write(nest_sep + nest_prefix)
            f.write(fmt % tuple(point.tolist()))
            f.write(nest_suffix)
        f.write(nest_suffix)
    else:
        # Use recursion for three or more dimensions:
        assert set.shape[0] > 0
        f.write(nest_prefix)
        write_array(f, set[0],
                    item_sep, nest_prefix, nest_suffix, nest_sep)
        for subset in set[1:]:
            f.write(nest_sep)
            write_array(f, subset,
                        item_sep, nest_prefix, nest_suffix, nest_sep)
        f.write(nest_suffix)


def grid_function(f, xvals, yvals, typecode = Numeric.Float32):
    """Compute a function on a grid.

    'xvals' and 'yvals' should be 1-D arrays listing the values of x
    and y at which f should be tabulated.  f should be a function
    taking two floating point arguments.  The return value is a matrix
    M where M[i,j] = f(xvals[i],yvals[j]), which can for example be
    used in the 'GridData' constructor.

    Note that f is evaluated at each pair of points using a Python
    loop, which can be slow if the number of points is large.  If
    speed is an issue, you should if possible compute functions
    matrix-wise using Numeric's built-in ufuncs.

    """

    m = Numeric.zeros((len(xvals), len(yvals)), typecode=typecode)
    for xi in range(len(xvals)):
        x = xvals[xi]
        for yi in range(len(yvals)):
            y = yvals[yi]
            m[xi,yi] = f(x,y)
    return m


class OptionException(Exception):
    """raised for unrecognized option(s)"""
    pass

class DataException(Exception):
    """raised for data in the wrong format"""
    pass


class PlotItem:
    """Plotitem represents an item that can be plotted by gnuplot.

    For the finest control over the output, you can create the
    PlotItems yourself with additional keyword options, or derive new
    classes from PlotItem.

    Options:
      with=<string> -- choose how item will be plotted, e.g.,
                       with='points 3 3'.
      title=<string> -- set the title to be associated with the item
                        in the plot legend.
      title=None -- choose `notitle' option (omit item from legend).

    Note that omitting the title option is different than setting
    `title=None'; the former chooses gnuplot's default whereas the
    latter chooses `notitle'.

    Members:
    
      '_basecommand' -- a string holding the elementary argument that
                        must be passed to gnuplot's `plot' command for
                        this item; e.g., 'sin(x)' or '"filename.dat"'.
      '_options' -- a dictionary of (<option>,<string>) tuples
                    corresponding to the plot options that have been
                    specified for this object.  <option> is the option
                    as specified by the user; <string> is the string
                    that needs to be set in the command line to set
                    that option (or None if no string is needed).
                    E.g., {'title':'Data', 'with':'linespoints'}.

    """

    def __init__(self, basecommand, **keyw):
        self._basecommand = basecommand
        self._options = {}
        apply(self.set_option, (), keyw)

    def get_option(self, name):
        try:
            return self._options[name][0]
        except:
            raise KeyError('option %s is not set!' % name)

    def set_option(self, with=_unset, title=_unset, **keyw):
        if with is not _unset:
            if with is None:
                self._options['with'] = (None, None)
            elif type(with) is type(''):
                self._options['with'] = (with, 'with %s' % with)
            else:
                OptionException('with=%s' % (with,))
        if title is not _unset:
            if title is None:
                self._options['title'] = (None, 'notitle')
            elif type(title) is type(''):
                self._options['title'] = (title, 'title "%s"' % title)
            else:
                OptionException('title=%s' % (title,))
        if keyw:
            # one or more unrecognized options; give error for one of them:
            (name,value) = keyw.items()[0]
            raise OptionException('%s=%s' % (name,value))

    def clear_option(self, name):
        """Clear (unset) a plot option."""

        try:
            del self._options[name]
        except KeyError:
            pass

    # order in which options need to be passed to gnuplot:
    _option_sequence = ['binary', 'using', 'title', 'with']

    def command(self):
        """Build the 'plot' command to be sent to gnuplot.

        Build and return the 'plot' command, with options, necessary
        to display this item.

        """

        cmd = [self._basecommand]
        for opt in self._option_sequence:
            (val,str) = self._options.get(opt, (None,None))
            if str is not None:
                cmd.append(str)
        return string.join(cmd)

    # if the plot command requires data to be put on stdin (i.e.,
    # `plot "-"'), this method should put that data there.
    def pipein(self, file):
        pass


class Func(PlotItem):
    """Represents a mathematical expression to plot.

    Func represents a mathematical expression that is to be computed by
    gnuplot itself, as if you would type

        gnuplot> plot sin(x)

    into gnuplot itself.  The argument to the contructor is a string
    that should be a mathematical expression.  Example:

        g.plot(Func('sin(x)', with='line 3'))

    or a shorthand example:

        g.plot('sin(x)')

    """

    # The PlotItem constructor does what we need.
    pass


class AnyFile:
    """An AnyFile represents any kind of file to be used by gnuplot.

    An AnyFile represents a file, but presumably one that holds data
    in a format readable by gnuplot.  This class simply remembers the
    filename; the existence and format of the file are not checked
    whatsoever.  If no filename is specfied, a random one is created.
    Note that this is not a PlotItem, though it is used by the 'File'
    PlotItem.  Members:

        self.filename -- the filename of the file

    """

    def __init__(self, filename=None):
        if filename is None:
            filename = tempfile.mktemp()
        self.filename = filename


class TempFile(AnyFile):
    """A TempFile is a file that is automatically deleted.

    A TempFile points to a file.  The file is deleted automatically
    when the TempFile object is deleted.

    The constructor is inherited from AnyFile.  It can be passed a
    filename or nothing (in which case a random filename is chosen).

    WARNING: whatever filename you pass to the constructor **WILL BE
    DELETED** when the TempFile object is deleted, even if it was a
    pre-existing file! This is intended to be used as a parent class of
    TempArrayFile.

    """

    def __del__(self):
        os.unlink(self.filename)


class ArrayFile(AnyFile):
    """A file to which, upon creation, an array is written.

    When an ArrayFile is constructed, it creates a file and fills it
    with the contents of a 2-d or 3-d Numeric array in the format
    expected by gnuplot (see write_array for details).  The filename
    can be specified, otherwise a random filename is chosen.  The file
    is NOT deleted automatically.

    """

    def __init__(self, set, filename=None):
        AnyFile.__init__(self, filename)
        write_array(open(self.filename, 'w'), set)


class TempArrayFile(ArrayFile, TempFile):
    """An ArrayFile that is deleted automatically."""

    def __init__(self, set, filename=None):
        ArrayFile.__init__(self, set, filename)


class File(PlotItem):
    """A PlotItem representing a file that contains gnuplot data."""

    def __init__(self, file, **keyw):
        """Construct a File object.

        '<file>' can be either a string holding the filename of an
        existing file, or it can be an object of any class derived
        from 'AnyFile' (such as a 'TempArrayFile').  Keyword arguments
        recognized (in addition to those recognized by 'PlotItem'):

            'using=<int>' -- plot that column against line number
            'using=<tuple>' -- plot using a:b:c:d etc.
            'using=<string>' -- plot `using <string>' (allows gnuplot's
                                arbitrary column arithmetic)
            'binary=<boolean>' -- data in file is in binary format
                                  (only recognized for grid data for
                                  splot).

        Note that the 'using' option is interpreted by gnuplot, so
        columns must be numbered starting with 1.  The default 'title'
        for a TempFile is 'notitle' to avoid using the temporary
        file's name as the title.

        """

        if isinstance(file, AnyFile):
            self.file = file
            # If no title is specified, then use `notitle' for
            # TempFiles (to avoid using the temporary filename as the
            # title.)
            if isinstance(file, TempFile) and not keyw.has_key('title'):
                keyw['title'] = None
        elif type(file) is type(''):
            self.file = AnyFile(file)
        else:
            raise OptionException
        # Use single-quotes so that pgnuplot can handle DOS filenames:
        apply(PlotItem.__init__, (self, "'%s'" % self.file.filename), keyw)

    def set_option(self, using=_unset, binary=_unset, **keyw):
        if using is not _unset:
            if using is None:
                self.clear_option('using')
            elif type(using) in [type(''), type(1)]:
                self._options['using'] = (using, 'using %s' % using)
            elif type(using) is type(()):
                self._options['using'] = (using,
                                          'using %s' %
                                          string.join(map(repr, using), ':'))
            else:
                raise OptionException('using=%s' % (using,))
        if binary is not _unset:
            if binary:
                assert _recognizes_binary_splot, \
                       OptionException('Gnuplot.py is currently configured to '
                                       'reject binary data!')
                self._options['binary'] = (1, 'binary')
            else:
                self._options['binary'] = (0, None)
        apply(PlotItem.set_option, (self,), keyw)


class Data(PlotItem):
    """Represents data from memory to be plotted with Gnuplot.

    Takes a numeric array from memory and outputs it to a temporary
    file that can be plotted by gnuplot.

    """

    def __init__(self, *set, **keyw):
        """Construct a Data object from a numeric array.

        Create a Data object (which is a type of PlotItem) out of one
        or more Float Python Numeric arrays (or objects that can be
        converted to a Float Numeric array).  If the routine is passed
        one array, the last index ranges over the values comprising a
        single data point (e.g., [x, y, and sigma]) and the rest of
        the indices select the data point.  If the routine is passed
        more than one array, they must have identical shapes, and then
        each data point is composed of one point from each array.
        I.e., 'Data(x,x**2)' is a PlotItem that represents x squared
        as a function of x.  For the output format, see the comments
        in ArrayFile.

        The array is first written to a temporary file, then that file
        is plotted.  Keyword arguments recognized (in addition to those
        recognized by PlotItem):

            cols=<tuple> -- write only the specified columns from each
                            data point to the file.  Since cols is
                            used by python, the columns should be
                            numbered in the python style (starting
                            from 0), not the gnuplot style (starting
                            from 1).

        The data are immediately written to the temp file; no copy is
        kept in memory.

        """

        if len(set) == 1:
            # set was passed as a single structure
            set = float_array(set[0])
        else:
            # set was passed column by column (for example,
            # Data(x,y)); pack it into one big array (this will test
            # that sizes are all the same):
            set = float_array(set)
            dims = len(set.shape)
            # transpose so that the last index selects x vs. y:
            set = Numeric.transpose(set, (dims-1,) + tuple(range(dims-1)))
        if keyw.has_key('cols'):
            cols = keyw['cols']
            del keyw['cols']
            if type(cols) is type(1):
                cols = (cols,)
            set = Numeric.take(set, cols, -1)

        self.file = TempArrayFile(set)

        # If no title is specified, then use `notitle' (to avoid using
        # the temporary filename as the title).
        if not keyw.has_key('title'):
            keyw['title'] = None
        apply(PlotItem.__init__, (self, "'%s'" % self.file.filename), keyw)

    def set_option(self, cols=_unset, **keyw):
        if cols is not _unset:
            raise OptionException('Cannot modify cols option!')
        else:
            apply(PlotItem.set_option, (self,), keyw)


class GridData(PlotItem):
    """Holds data representing a function of two variables, for use in splot.

    GridData represents a function that has been tabulated on a
    rectangular grid.  It is a PlotItem, so GridData objects can be
    plotted by Gnuplot.  The data are written to a file but not stored
    in memory.

    If binary=1 is passed to the constructor, the data will be passed
    to gnuplot in binary format and the `binary' option added to the
    splot command line.  Binary format is faster and usually saves
    disk space but is not human-readable.  If your version of gnuplot
    doesn't support binary format (it is a recently-added feature), it
    can be disabled by setting the configuration variable
    _recognizes_binary_splot=0 at the top of this file.

    """

    def __init__(self, toplot, xvals=None, yvals=None, binary=1, **keyw):
        """GridData constructor.

        Arguments:

            'toplot' -- the thing to plot: a 2-d array with dimensions
                        (numx,numy), OR callable object for which
                        toplot(x,y) returns a number.
            'xvals' -- a 1-d array with dimension (numx)
            'yvals' -- a 1-d array with dimension (numy)

        'toplot' can be a data array, in which case it should hold the
        values of a function f(x,y) tabulated on a grid of points,
        such that 'toplot[i,j] == f(xvals[i], yvals[j])'.  If 'xvals'
        and/or 'yvals' are omitted, integers (starting with
        0) are used for that coordinate.  The data are written to a
        temporary file; no copy of the data is kept in memory.

        Alternatively 'toplot' can be a function object taking two
        arguments, in which case toplot(x,y) will be computed at all
        grid points with x and y taken from xvals and yvals
        respectively.

        If binary=0 then the data are written to a datafile as 'x y
        f(x,y)' triplets that can be used by gnuplot's splot command.
        If binary=1 then the data are written to a file in a binary
        format that splot can understand.

        Thus if you have three arrays in the above format and a
        Gnuplot instance called g, you can plot your data by typing
        for example:

            g.splot(Gnuplot.GridData(data,xvals,yvals))

        """

        try:
            # Try to interpret data as an array:
            data = float_array(toplot)
        except TypeError:
            # That didn't work; try to interpret data as a callable
            # object with arguments (x,y):
            xvals = float_array(xvals)
            (numx,) = xvals.shape

            yvals = float_array(yvals)
            (numy,) = yvals.shape

            # try evaluating with Numeric.  This will work if the
            # function is implemented only in terms of Numeric ufuncs
            # (functions and operators for which matrix-wise
            # evaluation is defined).
            try:
                data = toplot(xvals,yvals)
            except:
                # that didn't work; evaluate via a python loop:
                data = grid_function(toplot, xvals, yvals)
        else:
            assert len(data.shape) == 2
            (numx, numy) = data.shape

            if xvals is None:
                xvals = Numeric.arange(numx)
            else:
                xvals = float_array(xvals)
                assert xvals.shape == (numx,)

            if yvals is None:
                yvals = Numeric.arange(numy)
            else:
                yvals = float_array(yvals)
                assert yvals.shape == (numy,)

        # xvals, yvals, and data are now all filled with arrays of data.
        if binary and _recognizes_binary_splot:
            # write file in binary format
            mout = Numeric.zeros((numx + 1, numy + 1), Numeric.Float32)
            mout[0,0] = numy
            mout[0,1:] = yvals.astype(Numeric.Float32)
            mout[1:,0] = xvals.astype(Numeric.Float32)
            try:
                # try copying without the additional copy implied by astype():
                mout[1:,1:] = data
            except:
                # if that didn't work then downcasting from double
                # must be necessary:
                mout[1:,1:] = data.astype(Numeric.Float32)
            self.file = TempFile()
            open(self.file.filename, 'wb').write(mout.tostring())

            # avoid using the temporary filename as the title:
            if not keyw.has_key('title'):
                keyw['title'] = None
            apply(PlotItem.__init__, (self, "'%s'" % self.file.filename), keyw)

            # Include the command-line option to read in binary data:
            self._options['binary'] = (1, 'binary')
        else:
            # output data to file as "x y f(x)" triplets.  This
            # requires numy copies of each x value and numx copies of
            # each y value.  First reformat the data:
            set = Numeric.transpose(
                Numeric.array(
                    (Numeric.transpose(Numeric.resize(xvals, (numy, numx))),
                     Numeric.resize(yvals, (numx, numy)),
                     data)), (1,2,0))
            # now just output the data with the usual routine.  This
            # will produce data properly formatted in blocks separated
            # by blank lines so that gnuplot can connect the points
            # into a grid.
            self.file = TempArrayFile(set)
            # avoid using the temporary filename as the title:
            if not keyw.has_key('title'):
                keyw['title'] = None
            apply(PlotItem.__init__, (self, "'%s'" % self.file.filename), keyw)
            self._options['binary'] = (0, None)

    def set_option(self, binary=_unset, **keyw):
        if binary is not _unset:
            raise OptionException('Cannot modify binary option!')
        apply(PlotItem.set_option, (self,), keyw)


class Gnuplot:
    """gnuplot plotting object.

    A Gnuplot represents a running gnuplot program and a pipe to
    communicate with it.  It keeps a reference to each of the
    PlotItems used in the current plot, so that they (and their
    associated temporary files) are not deleted prematurely.  The
    communication is one-way; gnuplot's text output just goes to
    stdout with no attempt to check it for error messages.

    Members:

    'gnuplot' -- the pipe to gnuplot or a file gathering the commands
    'itemlist' -- a list of the PlotItems that are associated with the
                  current plot.  These are deleted whenever a new plot
                  command is issued via the `plot' method.
    'debug' -- if this flag is set, commands sent to gnuplot will also
               be echoed to stderr.
    'plotcmd' -- 'plot' or 'splot', depending on what was the last
                 plot command.

    Methods:

    '__init__' -- if a filename argument is specified, the commands
                  will be written to that file instead of being piped
                  to gnuplot immediately.
    'plot' -- clear the old plot and old PlotItems, then plot the
              arguments in a fresh plot command.  Arguments can be: a
              PlotItem, which is plotted along with its internal
              options; a string, which is plotted as a Func; or
              anything else, which is plotted as a Data.
    'hardcopy' -- replot the plot to a postscript file (if filename
                  argument is specified) or pipe it to lpr othewise.
                  If the option `color' is set to true, then output
                  color postscript.
    'replot' -- replot the old items, adding any arguments as
                additional items as in the plot method.
    'refresh' -- issue (or reissue) the plot command using the current
                 PlotItems.
    '__call__' -- pass an arbitrary string to the gnuplot process,
                  followed by a newline.
    'xlabel', 'ylabel', 'title' -- set attribute to be a string.
    'interact' -- read lines from stdin and send them, one by one, to
                  the gnuplot interpreter.  Basically you can type
                  commands directly to the gnuplot command processor
                  (though without command-line editing).
    'load' -- load a file (using the gnuplot `load' command).
    'save' -- save gnuplot commands to a file (using gnuplot `save'
              command) If any of the PlotItems is a temporary file, it
              will be deleted at the usual time and the save file might
              be pretty useless :-).
    'clear' -- clear the plot window (but not the itemlist).
    'reset' -- reset all gnuplot settings to their defaults and clear
               the current itemlist.
    'set_string' -- set or unset a gnuplot option whose value is a
                    string.
    '_clear_queue' -- clear the current PlotItem list.
    '_add_to_queue' -- add the specified items to the current
                       PlotItem list.

    """

    def __init__(self, filename=None, persist=0, debug=0):
        """Create a Gnuplot object.

        'Gnuplot(filename=None, persist=0, debug=0)':

        Create a 'Gnuplot' object.  By default, this starts a gnuplot
        process and prepares to write commands to it.  If 'filename'
        is specified, the commands are instead written to that file
        (i.e., for later use using 'load').  If 'persist' is set,
        gnuplot will be started with the '-persist' option (which
        creates a new X11 plot window for each plot command).  (This
        option is not available on older versions of gnuplot.)  If
        'debug' is set, the gnuplot commands are echoed to stderr as
        well as being send to gnuplot.

        """

        if filename:
            # put gnuplot commands into a file:
            self.gnuplot = open(filename, 'w')
        else:
            if persist:
                if not test_persist():
                    raise OptionException(
                        '-persist does not seem to be supported '
                        'by your version of gnuplot!')
                self.gnuplot = popen('%s -persist' % _gnuplot_command, 'w')
            else:
                self.gnuplot = popen(_gnuplot_command, 'w')
        self._clear_queue()
        self.debug = debug
        self.plotcmd = 'plot'

    def __del__(self):
        self('quit')
        self.gnuplot.close()

    def __call__(self, s):
        """Send a command string to gnuplot.

        '__call__(s)': send the string s as a command to gnuplot,
        followed by a newline and flush.  All interaction with the
        gnuplot process is through this method.

        """

        self.gnuplot.write(s + '\n')
        self.gnuplot.flush()
        if self.debug:
            # also echo to stderr for user to see:
            sys.stderr.write('gnuplot> %s\n' % (s,))

    def refresh(self):
        """Refresh the plot, using the current PlotItems.

        Refresh the current plot by reissuing the gnuplot plot command
        corresponding to the current itemlist.

        """

        plotcmds = []
        for item in self.itemlist:
            plotcmds.append(item.command())
        self(self.plotcmd + ' ' + string.join(plotcmds, ', '))
        for item in self.itemlist:
            item.pipein(self.gnuplot)

    def _clear_queue(self):
        """Clear the PlotItems from the queue."""

        self.itemlist = []

    def _add_to_queue(self, items):
        """Add a list of items to the itemlist, but don't plot them.

        'items' is a list or tuple of items, each of which should be a
        'PlotItem' of some kind, a string (interpreted as a function
        string for gnuplot to evaluate), or a Numeric array (or
        something that can be converted to a Numeric array).

        """

        for item in items:
            if isinstance(item, PlotItem):
                self.itemlist.append(item)
            elif type(item) is type(''):
                self.itemlist.append(Func(item))
            else:
                # assume data is an array:
                self.itemlist.append(Data(item))

    def plot(self, *items):
        """Draw a new plot.

        'plot(item, ...)': Clear the current plot and create a new 2-d
        plot containing the specified items.  Arguments can be of the
        following types:

        'PlotItem' (e.g., 'Data', 'File', 'Func') -- This is the most
                   flexible way to call plot because the PlotItems can
                   contain suboptions.  Moreover, PlotItems can be
                   saved to variables so that their lifetime is longer
                   than one plot command--thus they can be replotted
                   with minimal overhead.

        'string' (i.e., 'sin(x)') -- The string is interpreted as
                 'Func(string)' (a function that is computed by
                 gnuplot).

        Anything else -- The object, which should be convertible to an
                         array, is converted to a Data() item, and
                         thus plotted as data.  If the conversion
                         fails, an exception is raised.

        """

        # remove old files:
        self.plotcmd = 'plot'
        self._clear_queue()
        self._add_to_queue(items)
        self.refresh()

    def splot(self, *items):
        """Draw a new three-dimensional plot.

        'splot(item, ...)' -- Clear the current plot and create a new
                3-d plot containing the specified items.  Arguments can
                be of the following types:
        'PlotItem' (e.g., 'Data', 'File', 'Func', 'GridData' ) -- This
                is the most flexible way to call plot because the
                PlotItems can contain suboptions.  Moreover, PlotItems
                can be saved to variables so that their lifetime is
                longer than one plot command--thus they can be
                replotted with minimal overhead.

        'string' (i.e., 'sin(x*y)') -- The string is interpreted as a
                'Func()' (a function that is computed by gnuplot).

        Anything else -- The object is converted to a Data() item, and
                thus plotted as data.  Note that each data point
                should normally have at least three values associated
                with it (i.e., x, y, and z).  If the conversion fails,
                an exception is raised.

        """

        # remove old files:
        self.plotcmd = 'splot'
        self._clear_queue()
        self._add_to_queue(items)
        self.refresh()

    def replot(self, *items):
        """Replot the data, possibly adding new PlotItems.

        Replot the existing graph, using the items in the current
        itemlist.  If arguments are specified, they are interpreted as
        additional items to be plotted alongside the existing items on
        the same graph.  See 'plot' for details.

        """

        self._add_to_queue(items)
        self.refresh()

    def interact(self):
        """Allow user to type arbitrary commands to gnuplot.

        Read stdin, line by line, and send each line as a command to
        gnuplot.  End by typing C-d.

        """

        sys.stderr.write('Press C-d to end interactive input\n')
        while 1:
            sys.stderr.write('gnuplot>>> ')
            line = sys.stdin.readline()
            if not line:
                break
            if line[-1] == '\n': line = line[:-1]
            self(line)

    def clear(self):
        """Clear the plot window (without affecting the current itemlist)."""

        self('clear')

    def reset(self):
        """Reset all gnuplot settings to their defaults and clear itemlist."""

        self('reset')
        self.itemlist = []

    def load(self, filename):
        """Load a file using gnuplot's `load' command."""

        self("load '%s'" % (filename,))

    def save(self, filename):
        """Save the current plot commands using gnuplot's `save' command."""

        self("save '%s'" % (filename,))

    def set_string(self, option, s=None):
        """Set a string option, or if s is omitted, unset the option."""

        if s is None:
            self('set %s' % (option,))
        else:
            self('set %s "%s"' % (option, s))

    def xlabel(self, s=None):
        """Set the plot's xlabel."""

        self.set_string('xlabel', s)

    def ylabel(self, s=None):
        """Set the plot's ylabel."""

        self.set_string('ylabel', s)

    def title(self, s=None):
        """Set the plot's title."""

        self.set_string('title', s)

    def hardcopy(self, filename=None, eps=0, color=0, enhanced=1):
        """Create a hardcopy of the current plot.

        Create a postscript hardcopy of the current plot.  If a
        filename is specified, save the output in that file; otherwise
        print it immediately using lpr.  If eps is specified, generate
        encapsulated postscript.  If color is specified, create a
        color plot.  If enhanced is specified (the default), then
        generate enhanced postscript.  (Some old gnuplot versions do
        not support enhanced postscript; if this is the case set
        enhanced=0.)  Note that this command will return immediately
        even though it might take gnuplot a while to actually finish
        working.

        """

        if filename is None:
            filename = _default_lpr
        setterm = ['set', 'term', 'postscript']
        if eps: setterm.append('eps')
        else: setterm.append('default')
        if enhanced: setterm.append('enhanced')
        if color: setterm.append('color')
        self(string.join(setterm))
        self.set_string('output', filename)
        self.refresh()
        self('set term %s' % _default_term)
        self.set_string('output')


# The following is a command defined for compatibility with Hinson's
# old Gnuplot.py module.  Its use is deprecated.

# When the plot command is called and persist is not available, the
# plotters will be stored here to prevent their being closed:
_gnuplot_processes = []

def plot(*items, **keyw):
    """plot data using gnuplot through Gnuplot.

    This command is roughly compatible with old Gnuplot plot command.
    It is provided for backwards compatibility with the old functional
    interface only.  It is recommended that you use the new
    object-oriented Gnuplot interface, which is much more flexible.

    It can only plot Numeric array data.  In this routine an NxM array
    is plotted as M-1 separate datasets, using columns 1:2, 1:3, ...,
    1:M.

    Limitations:

        - If persist is not available, the temporary files are not
          deleted until final python cleanup.

    """

    newitems = []
    for item in items:
        # assume data is an array:
        item = float_array(item)
        dim = len(item.shape)
        if dim == 1:
            newitems.append(Data(item[:, Numeric.NewAxis], with='lines'))
        elif dim == 2:
            if item.shape[1] == 1:
                # one column; just store one item for tempfile:
                newitems.append(Data(item, with='lines'))
            else:
                # more than one column; store item for each 1:2, 1:3, etc.
                tempf = TempArrayFile(item)
                for col in range(1, item.shape[1]):
                    newitems.append(File(tempf, using=(1,col+1), with='lines'))
        else:
            raise DataException('Data array must be 1 or 2 dimensional')
    items = tuple(newitems)
    del newitems

    if keyw.has_key('file'):
        g = Gnuplot()
        # setup plot without actually plotting (so data don't appear
        # on the screen):
        g._add_to_queue(items)
        g.hardcopy(keyw['file'])
        # process will be closed automatically
    elif test_persist():
        g = Gnuplot(persist=1)
        apply(g.plot, items)
        # process will be closed automatically
    else:
        g = Gnuplot()
        apply(g.plot, items)
        # prevent process from being deleted:
        _gnuplot_processes.append(g)


def demo():
    """Demonstrate the package."""

    from Numeric import *
    import sys

    # A straightforward use of gnuplot.  The `debug=1' switch is used
    # in these examples so that the commands that are sent to gnuplot
    # are also output on stderr.
    g1 = Gnuplot(debug=1)
    g1.title('A simple example') # (optional)
    g1('set data style linespoints') # give gnuplot an arbitrary command
    # Plot a list of (x, y) pairs (tuples or a Numeric array would
    # also be OK):
    g1.plot([[0,1.1], [1,5.8], [2,3.3], [3,4.2]])

    # Plot one dataset from an array and one via a gnuplot function;
    # also demonstrate the use of item-specific options:
    g2 = Gnuplot(debug=1)
    x = arange(10, typecode=Float)
    y1 = x**2
    # Notice how this plotitem is created here but used later?  This
    # is convenient if the same dataset has to be plotted multiple
    # times.  It is also more efficient because the data need only be
    # written to a temporary file once.
    d = Data(x, y1,
             title='calculated by python',
             with='points 3 3')
    g2.title('Data can be computed by python or gnuplot')
    g2.xlabel('x')
    g2.ylabel('x squared')
    # Plot a function alongside the Data PlotItem defined above:
    g2.plot(Func('x**2', title='calculated by gnuplot'), d)

    # Save what we just plotted as a color postscript file.

    # With the enhanced postscript option, it is possible to show `x
    # squared' with a superscript (plus much, much more; see `help set
    # term postscript' in the gnuplot docs).  If your gnuplot doesn't
    # support enhanced mode, set `enhanced=0' below.
    g2.ylabel('x^2') # take advantage of enhanced postscript mode
    print ('\n******** Generating postscript file '
           '"gnuplot_test_plot.ps" ********\n')
    g2.hardcopy('gnuplot_test_plot.ps', enhanced=1, color=1)

    # Demonstrate a 3-d plot:
    g3 = Gnuplot(debug=1)
    # set up x and y values at which the function will be tabulated:
    x = arange(35)/2.0
    y = arange(30)/10.0 - 1.5
    # Make a 2-d array containing a function of x and y.  First create
    # xm and ym which contain the x and y values in a matrix form that
    # can be `broadcast' into a matrix of the appropriate shape:
    xm = x[:,NewAxis]
    ym = y[NewAxis,:]
    m = (sin(xm) + 0.1*xm) - ym**2
    g3('set parametric')
    g3('set data style lines')
    g3('set hidden')
    g3('set contour base')
    g3.xlabel('x')
    g3.ylabel('y')
    # The `binary=1' option would cause communication with gnuplot to
    # be in binary format, which is considerably faster and uses less
    # disk space.  (This only works with the splot command due to
    # limitations of gnuplot.)  `binary=1' is the default, but here we
    # disable binary because older versions of gnuplot don't allow
    # binary data.  Change this to `binary=1' (or omit the binary
    # option) to get the advantage of binary format.
    g3.splot(GridData(m,x,y, binary=0))

    # Delay so the user can see the plots:
    sys.stderr.write('Three plots should have appeared on your screen '
                     '(they may be overlapping).\n')
    raw_input('Please press return to continue...\n')

    # ensure processes and temporary files are cleaned up:
    del g1, g2, g3, d

    # Enable the following code to test the old-style gnuplot interface
    if 0:
        # List of (x, y) pairs
        plot([(0.,1),(1.,5),(2.,3),(3.,4)])

        # List of y values, file output
        print '\n            Generating postscript file "gnuplot_test2.ps"\n'
        plot([1, 5, 3, 4], file='gnuplot_test2.ps')

        # Two plots; each given by a 2d array
        x = arange(10, typecode=Float)
        y1 = x**2
        y2 = (10-x)**2
        plot(transpose(array([x, y1])), transpose(array([x, y2])))


if __name__ == '__main__':
    demo()


