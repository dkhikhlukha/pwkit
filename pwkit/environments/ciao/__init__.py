# -*- mode: python; coding: utf-8 -*-
# Copyright 2016 Peter Williams <peter@newton.cx> and collaborators.
# Licensed under the MIT License.

"""ciao - running software in the CIAO environment

To use, export an environment variable $PWKIT_CIAO pointing to the CIAO
installation root.


Unpacking data sets
==========================

Data sets are provided as tar files. They unpack to a directory named by the
“obsid” which contains an ``oif.fits`` file and ``primary`` and ``secondary``
subdirectories.


CIAO installation notes
==========================

Download installer script from http://cxc.harvard.edu/ciao/download/. Select
some kind of parent directory like ``/soft/ciao`` for both downloading
tarballs and installing CIAO itself. This may also download and install the
large “caldb” data set. All of the files will end up in a subdirectory such as
``/soft/ciao/ciao-4.8``.

"""
from __future__ import absolute_import, division, print_function, unicode_literals

__all__ = str ('CiaoEnvironment CiaoTool').split ()

import io, six

from ... import PKError, cli
from ...cli import multitool
from ...io import Path
from .. import Environment, prepend_environ_path, user_data_path


class CiaoEnvironment (Environment):
    _installpath = None
    _parampath = None

    def __init__ (self, installdir=None, paramdir=None):
        if installdir is None:
            installdir = self._default_installdir ()
        if paramdir is None:
            paramdir = user_data_path ('cxcds_param')

        self._installpath = Path (installdir).absolute ()
        self._parampath = Path (paramdir).absolute ()


    def _default_installdir (self):
        import os
        d = os.environ.get ('PWKIT_CIAO')
        if d is None:
            raise PKError ('CIAO installation directory must be specified '
                           'in the $PWKIT_CIAO environment variable')
        return d


    def modify_environment (self, env):
        p = self._installpath

        env[b'ASCDS_INSTALL'] = str (p)
        env[b'ASCDS_CONTRIB'] = str (p / 'contrib')
        env[b'ASCDS_BIN'] = str (p / 'bin')
        env[b'ASCDS_LIB'] = str (p / 'lib')
        env[b'ASCDS_IMAGER_PATH'] = str (p / 'ots' / 'bin')
        env[b'CIAO_XPA'] = b'CIAO'
        env[b'CIAO_PYTHON'] = b'CIAO'
        env[b'CIAO_APP_PYTHON'] = b'CIAO'
        env[b'CIAO_IPYTHON'] = b'CIAO'
        env[b'CIAO_APP_IPYTHON'] = b'CIAO'
        env[b'CIAO_PYTHON_EXE'] = str (p / 'ots' / 'bin' / 'python')
        env[b'CIAO_SCRIPT_LANG'] = b'python'
        env[b'XPA_METHOD'] = b'local'
        env[b'CALDB'] = str (p / 'CALDB')
        env[b'CALDBCONFIG'] = str (p / 'CALDB' / 'software' / 'tools' / 'caldb.config')
        env[b'CALDBALIAS'] = str (p / 'CALDB' / 'software' / 'tools' / 'alias_config.fits')
        env[b'ASCDS_CALIB'] = str (p / 'data')
        env[b'ASCDS_CIAO'] = b'ciao'

        # Obsvis:
        env[b'OBSVIS_PKG_PATH'] = str (p / 'lib' / 'tcltk' / 'packages' / 'obsvis')

        # Sherpa:
        env[b'CIAO_HEADAS'] = str (p / 'ots' / 'spectral')
        env[b'XSPEC_HELP_FILE'] = str (p / 'doc' / 'xspec.hlp')

        # Proposal tools:
        env[b'DATA_ROOT'] = str (p / 'config')
        env[b'JCMLIBDATA'] = str (p / 'config' / 'jcm_data')
        env[b'ASCDS_PROP_NHBASE'] = env[b'JCMLIBDATA']
        env[b'JCMPATH'] = env[b'JCMLIBDATA']
        env[b'ASCDS_PROP_DATE_DATA'] = env[b'JCMLIBDATA']
        env[b'ASCDS_PROP_PREC_DATA'] = env[b'JCMLIBDATA']

        env[b'PFILES'] = '%s;%s:%s' % (self._parampath,
                                       p / 'contrib' / 'param',
                                       p / 'param')

        prepend_environ_path (env, b'PATH', str (p / 'contrib' / 'bin'))
        prepend_environ_path (env, b'PATH', str (p / 'ots' / 'bin'))
        prepend_environ_path (env, b'PATH', str (p / 'bin'))

        return env

    def _preexec (self, env, **kwargs):
        self._parampath.ensure_dir (parents=True)


# Command-line interface

from .. import DefaultExecCommand, DefaultShellCommand

class CiaoTool (multitool.Multitool):
    cli_name = 'pkenvtool ciao'
    summary = 'Run tools in the CIAO environment.'

    def invoke_command (self, cmd, args, **kwargs):
        return super (CiaoTool, self).invoke_command (cmd, args,
                                                      envname='ciao',
                                                      envclass=CiaoEnvironment,
                                                      module=__package__,
                                                      **kwargs)


def commandline (argv):
    from six import itervalues
    tool = CiaoTool ()
    tool.populate (itervalues (globals ()))
    tool.commandline (argv)
