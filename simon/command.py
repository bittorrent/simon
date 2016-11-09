import logging
import sys

from pkg_resources import iter_entry_points

try:
    basestring
except NameError:
    basestring = str


def load_commands(module_name):
    try:
        components = module_name.split('.')
        module = __import__(module_name)
        for component in components[1:]:
            module = getattr(module, component)
        return {command.name(): command for command in module.commands()}
    except (AttributeError, ImportError):
        logging.warning('unable to load commands from {}'.format(module_name))
        return {}


def available_commands():
    ret = {key: value for name in [
        'simon.commands.cpp_analysis',
        'simon.commands.judge',
        'simon.commands.bincommands',
    ] for key, value in load_commands(name).items()}
    for entry_point in iter_entry_points(group='simon.commands'):
        for command in entry_point.load()():
            ret[command.name()] = command
    return ret


def execute(command, args, stdout=sys.stdout):
    original_stdout = sys.stdout
    sys.stdout = stdout
    try:
        return available_commands()[command].execute([arg if isinstance(arg, basestring) else str(arg) for arg in args])
    finally:
        sys.stdout = original_stdout


class Command:
    def name(self):
        raise NotImplementedError('name')

    def category(self):
        raise NotImplementedError('category')

    def short_description(self):
        raise NotImplementedError('short_description')

    def execute(self, configuration, args):
        raise NotImplementedError('execute')

    def show_help(self):
        print('Help for this command is not available. Good luck.')
        return 1
