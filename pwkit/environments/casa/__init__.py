# -*- mode: python; coding: utf-8 -*-
# Copyright 2015 Peter Williams <peter@newton.cx> and collaborators.
# Licensed under the MIT License.

"""casa - running software in the CASA environment

To use, export an environment variable $PWKIT_CASA pointing to the CASA
installation root. The files $PWKIT_CASA/asdm2MS and $PWKIT_CASA/casapy should
exist.

XXX untested with 32-bit, probably won't work.
XXX test only on Linux, probably needs work for Macs.


CASA installation notes
==========================

Download tarball as linked from http://casa.nrao.edu/casa_obtaining.shtml .
Tarball unpacks to some versioned subdirectory. The names and version codes
are highly variable and annoying.

"""
from __future__ import absolute_import, division, print_function, unicode_literals

__all__ = (b'CasaEnvironment CasaTool commandline').split ()

import glob, io, os.path

from ... import PKError, cli
from ...cli import multitool
from .. import Environment, prepend_environ_path, user_data_path


class CasaEnvironment (Environment):
    _rootdir = None

    def __init__ (self, rootdir=None):
        if rootdir is None:
            rootdir = self._default_rootdir ()

        self._rootdir = os.path.abspath (rootdir)


    def _default_rootdir (self):
        d = os.environ.get ('PWKIT_CASA')
        if d is None:
            raise PKError ('CASA installation directory must be specified '
                           'in the $PWKIT_CASA environment variable')
        return d


    def modify_environment (self, env):
        """Maintaining compatibility with different CASA versions is a pain."""

        def path (*args):
            return os.path.join (self._rootdir, *args)

        lib = 'lib64' if os.path.isdir (path ('lib64')) else 'lib'
        # 4.3.1 comes with both python2.6 and python2.7???
        pydir = sorted (glob.glob (path (lib, 'python2*')))[-1]

        tcldir = path ('share', 'tcl')
        if not os.path.isdir (tcldir):
            tcldir = glob.glob (path ('share', 'tcl*'))[-1]

        bindir = path (lib, 'casa', 'bin')
        if not os.path.isdir (bindir):
            bindir = path (lib, 'casapy', 'bin')

        env[b'CASAROOT'] = path ()
        env[b'CASAPATH'] = ' '.join ([path (),
                                      os.uname ()[0].lower (),
                                      'local',
                                      os.uname ()[1]])
        env[b'CASA_INSTALLATION_TYPE'] = b'tar-installation'
        env[b'CASA_INSTALLATION_DIRECTORY'] = env[b'CASAROOT']
        env[b'__CASAPY_PYTHONDIR'] = pydir
        env[b'MATPLOTLIBRC'] = path ('share', 'matplotlib')
        env[b'PYTHONHOME'] = env[b'CASAROOT']
        env[b'TCL_LIBRARY'] = tcldir
        env[b'TK_LIBRARY'] = path ('share', 'tk')
        env[b'QT_PLUGIN_PATH'] = path (lib, 'qt4', 'plugins')

        prepend_environ_path (env, b'PATH', bindir)
        prepend_environ_path (env, b'LD_LIBRARY_PATH', path (lib))
        # should we overwite PYTHONPATH instead?
        prepend_environ_path (env, b'PYTHONPATH', os.path.join (pydir, 'site-packages'))
        prepend_environ_path (env, b'PYTHONPATH', os.path.join (pydir, 'heuristics'))
        prepend_environ_path (env, b'PYTHONPATH', pydir)

        return env


# Command-line interface

from .. import DefaultExecCommand, DefaultShellCommand

class CasaTool (multitool.Multitool):
    cli_name = 'pkenvtool casa'
    summary = 'Run programs in the CASA environment.'

    def invoke_command (self, cmd, args, **kwargs):
        return super (CasaTool, self).invoke_command (cmd, args,
                                                      envname='casa',
                                                      envclass=CasaEnvironment,
                                                      module=__package__,
                                                      **kwargs)


def commandline (argv):
    tool = CasaTool ()
    tool.populate (globals ().itervalues ())
    tool.commandline (argv)