#!/usr/bin/env python
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

import os

from bypy.constants import (MAKEOPTS, PREFIX, PYTHON, build_dir, ismacos,
                            iswindows)
from bypy.utils import replace_in_file, run


def run_configure(for_webengine=False):
    b = build_dir()
    if ismacos:
        b = os.path.join(b, 'python/Python.framework/Versions/2.7')
    elif iswindows:
        b = os.path.join(b, 'private', 'python')
    lp = os.path.join(PREFIX, 'qt', 'lib')
    sip, qmake = 'sip', 'qmake'
    if iswindows:
        sip += '.exe'
        qmake += '.exe'
    sp = 'Lib' if iswindows else 'lib/python2.7'
    sip_dir = f'{b}/share/sip/PyQt5'
    dest_dir = f'{b}/{sp}/site-packages'
    if for_webengine:
        pyqt_options = []
        os.makedirs(sip_dir)
        dest_dir += '/PyQt5'
    else:
        pyqt_options = [
            '--confirm-license',
            '--assume-shared',
            f'--bindir={b}/bin',
            '--no-designer-plugin',
            '--no-qml-plugin',
        ]
    cmd = [PYTHON, 'configure.py'] + pyqt_options + [
        '--sip=%s/bin/%s' % (PREFIX, sip),
        '--qmake=%s/qt/bin/%s' % (PREFIX, qmake),
        f'--destdir={dest_dir}', '--verbose',
        f'--sipdir={sip_dir}', '--no-stubs', '-c', '-j5',
        '--no-docstrings',
    ]
    if iswindows:
        cmd.append('--spec=win32-msvc2015')
        cmd.append('--sip-incdir=%s/private/python/include' % PREFIX)
    run(*cmd, library_path=lp)


def run_build():
    if iswindows:
        # In VisualStudio 15 Update 3 the compiler crashes on the below
        # statement
        replace_in_file('QtGui/sipQtGuipart2.cpp',
                        'return new  ::QPicture[sipNrElem]', 'return NULL')
        run('nmake')
        run('nmake install')
    else:
        lp = os.path.join(PREFIX, 'qt', 'lib')
        run('make ' + MAKEOPTS, library_path=lp)
        run('make install', library_path=True)


def main(args):
    run_configure()
    run_build()


def post_install_check():
    run(PYTHON,
        '-c',
        'from PyQt5 import sip, QtCore, QtGui, QtWebKit',
        library_path=os.path.join(PREFIX, 'qt', 'lib'))
