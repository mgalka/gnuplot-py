# $Id$

"""gp_win32 -- an interface to gnuplot for Windows.

Copyright (C) 1999 Michael Haggerty

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

"""

__version__ = '1.3'
__cvs_version__ = '$Revision$'


# ############ Configuration variables: ################################

class GnuplotOpts:
    """The configuration options for gnuplot under windows.

    See gp.py for details about the meaning of these options.  Please
    let me know if you know better choices for these settings."""

    # Command to start up the gnuplot program.  Note that on windows
    # the main gnuplot program cannot be used directly because it can
    # not read commands from standard input.  See README for more
    # information.
    gnuplot_command = 'pgnuplot.exe'

    # The '-persist' option is not supported on windows:
    recognizes_persist = 0

    # As far as I know, gnuplot under windows can use binary data:
    recognizes_binary_splot = 1

    # Apparently gnuplot on windows can use inline data, but we use
    # non-inline data (i.e., temporary files) by default for no
    # special reason:
    prefer_inline_data = 0

    # The default choice for the 'set term' command (to display on
    # screen):
    default_term = 'windows'

    # Gee, I wonder if the following can be used to print directly to
    # a postscript printer under windows.  Anybody know?
    default_lpr = 'prn:'

# ############ End of configuration options ############################


from win32pipe import popen


class GnuplotProcess:
    """Unsophisticated interface to a running gnuplot program.

    See gp.GnuplotProcess for usage information.

    """

    def __init__(self, persist=0):
        """Start a gnuplot process.

        Create a 'GnuplotProcess' object.  This starts a gnuplot
        program and prepares to write commands to it.

        Keyword arguments:

          'persist' -- the '-persist' option is not supported under
                       Windows so this argument must be zero.

        """

        assert not persist, '-persist is not supported under Windows!'

        self.gnuplot = popen(GnuplotOpts.gnuplot_command, 'w')

        # forward write and flush methods:
        self.write = self.gnuplot.write
        self.flush = self.gnuplot.flush

    def __call__(self, s):
        """Send a command string to gnuplot, followed by newline."""

        self.write(s + '\n')
        self.flush()


