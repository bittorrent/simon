import argparse
import os
import subprocess
import jinja2
import yaml
import multiprocessing

from ..command import Command


def commands():
    return [JudgeCommand()]


class JudgeCommand(Command):
    def __init__(self):
        self.__arg_parser = argparse.ArgumentParser(
            description='invokes scripted judgement'
        )

        self.__arg_parser.add_argument('script',
                                       help='judgement script to run')
        self.__arg_parser.add_argument('-D', '--define',
                                       nargs='*',
                                       action='append',
                                       help='specify a variable to be passed to the jinja renderer')

    def name(self):
        return 'judge'

    def category(self):
        return 'auditing'

    def short_description(self):
        return 'executes scripted judgement'

    def execute(self, args):
        parameters = self.__arg_parser.parse_args(args)

        with open(parameters.script, 'r') as f:
            script_content = f.read()

        env = jinja2.Environment()
        template = env.from_string(script_content)
        if hasattr(parameters, 'define') and parameters.define:
            for defines in parameters.define:
                for define in defines:
                    parts = define.split('=', 1)
                    value = parts[1] if len(parts) >= 2 else 1
                    env.globals[parts[0]] = value
        configuration = yaml.load(template.render(cpu_count=multiprocessing.cpu_count()))

        return subprocess.call(['sh', '-c', '\n'.join(['set -ex'] + configuration['script'])])

    def show_help(self):
        self.__arg_parser.print_help()
        return 0
