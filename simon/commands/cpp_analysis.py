import appdirs
import argparse
import hashlib
import platform
import os
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile

from ..command import Command

from distutils.spawn import find_executable

try:
    import urllib.request as urllib2
except ImportError:
    import urllib2


def commands():
    return [CPPAnalysisCommand()]


class CPPAnalysisCommand(Command):
    def __init__(self):
        self.__arg_parser = argparse.ArgumentParser(
            description='Statically analyzes C++.'
        )
        self.__arg_parser.add_argument('build_command', nargs=argparse.REMAINDER)

    def name(self):
        return 'c++-analysis'

    def category(self):
        return 'auditing'

    def short_description(self):
        return 'statically analyzes c++'

    def execute(self, args):
        analyzer = 'Xcode' if sys.platform == 'darwin' else find_executable('clang++')
        if not analyzer:
            raise RuntimeError('analyzer not found!')

        scan_build = CPPAnalysisCommand.__prepare_scan_build_environment()

        print('using analyzer {}'.format(analyzer))

        parameters = self.__arg_parser.parse_args(args)
        checkers = CPPAnalysisCommand.__checkers()

        return subprocess.call(
            [scan_build, '--status-bugs', '--use-analyzer={}'.format(analyzer)] +
            ' '.join(['-enable-checker ' + checker for checker in checkers]).split() +
            parameters.build_command
        )

    @classmethod
    def __prepare_scan_build_environment(cls):
        cache_directory = os.path.join(appdirs.user_cache_dir('simon', 'BitTorrent'), 'cpp-analysis')
        expected_checksum = 'f5b1f1e7348e415736559c36a59266ee80b57e4d'
        analyzer = os.path.join(cache_directory, expected_checksum)

        if not os.path.exists(analyzer):
            try:
                print('downloading clang-analyzer...')
                download = urllib2.urlopen('http://clang-analyzer.llvm.org/downloads/checker-277.tar.bz2')
                download_file = tempfile.TemporaryFile()
                contents = download.read()
                if hashlib.sha1(contents).hexdigest() != expected_checksum:
                    print('checksum verification failed')
                    return 1
                download_file.write(contents)
                download_file.seek(0)
                tar = tarfile.open(fileobj=download_file, mode='r|*')
                os.makedirs(analyzer)
                tar.extractall(analyzer)
                del tar
            except:
                if os.path.exists(analyzer):
                    shutil.rmtree(analyzer)
                raise

        analyzer = os.path.join(analyzer, 'checker-277')

        # for things like b2 toolsets that like to hard-code invocation commands :(
        wrapper_directory = os.path.abspath(os.path.join(analyzer, '..', 'wrappers'))
        if not os.path.exists(wrapper_directory):
            os.makedirs(wrapper_directory)
        os.environ['PATH'] = wrapper_directory + ':' + os.environ['PATH']
        for command, proxy in {
            'clang': 'ccc-analyzer',
            'clang++': 'c++-analyzer',
            'gcc': 'ccc-analyzer',
            'g++': 'c++-analyzer'
        }.items():
            path = os.path.join(wrapper_directory, command)
            with open(path, 'w') as f:
                f.write('#!/bin/sh\nPATH=$(echo $PATH | sed -e "s#{wrappers}:##g") {libexec}/{proxy} "$@"'.format(
                    libexec=os.path.join(analyzer, 'libexec'),
                    wrappers=wrapper_directory,
                    proxy=proxy))
            os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC)

        os.environ['CCC_CC'] = os.environ['CC'] if 'CC' in os.environ else 'clang'
        os.environ['CCC_CXX'] = os.environ['CXX'] if 'CXX' in os.environ else 'clang++'

        return os.path.join(analyzer, 'scan-build')

    @classmethod
    def __checkers(cls):
        checkers = [
            'alpha.core.BoolAssignment',
            'alpha.core.CallAndMessageUnInitRefArg',
            'alpha.core.CastSize',
            'alpha.core.FixedAddr',
            'alpha.core.PointerArithm',
            'alpha.core.PointerSub',
            'alpha.core.SizeofPtr',
            'alpha.core.TestAfterDivZero',
            'alpha.cplusplus.VirtualCall',
            'alpha.security.ArrayBoundV2',
            'alpha.security.ReturnPtrRange',
            'alpha.security.taint.TaintPropagation',
            'alpha.unix.Chroot',
            'alpha.unix.PthreadLock',
            'alpha.unix.SimpleStream',
            'alpha.unix.cstring.BufferOverlap',
            'alpha.unix.cstring.NotNullTerminated',
            'alpha.unix.cstring.OutOfBounds',
            'llvm.Conventions',
            'security.FloatLoopCounter',
            'security.insecureAPI.rand',
        ]

        if sys.platform == 'darwin':
            checkers.extend([
                'alpha.osx.cocoa.DirectIvarAssignment',
                'alpha.osx.cocoa.DirectIvarAssignmentForAnnotatedFunctions',
                'alpha.osx.cocoa.InstanceVariableInvalidation',
                'alpha.osx.cocoa.MissingInvalidationMethod',
            ])

        return checkers

    def show_help(self):
        self.__arg_parser.print_help()
        return 0
