import os
import pkg_resources
import subprocess

from ..command import Command


class BinCommand(Command):
    def __init__(self, name, bin_name, short_description, has_help=False):
        self.__name = name
        self.__bin_name = bin_name
        self.__short_description = short_description
        self.__has_help = has_help

    def name(self):
        return self.__name

    def category(self):
        return 'auditing'

    def short_description(self):
        return self.__short_description

    def execute(self, args):
        try:
            path = pkg_resources.resource_filename('simon', os.path.join('data', 'bin', self.__bin_name))
            subprocess.check_call([path] + args)
            return 0
        except subprocess.CalledProcessError:
            return 1
        except KeyboardInterrupt:
            return 1

    def show_help(self):
        if self.__has_help:
            return self.execute(None, ['--help'])
        else:
            return Command.show_help(self)


def commands():
    return [
        BinCommand('distribution-test',
                   bin_name='distribution-test',
                   short_description='tests various aspects of a distribution',
                   has_help=True),
        BinCommand('license',
                   bin_name='license',
                   short_description='manipulates licenses'),
    ]
