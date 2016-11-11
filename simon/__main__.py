import argparse
import logging
import os
import sys

from .command import available_commands, execute


def main(args=sys.argv):
    logging.basicConfig(level=logging.ERROR)
    commands = available_commands()

    command_categories = {}
    max_command_name_length = 0
    for command_name, command in sorted(commands.items()):
        if len(command_name) > max_command_name_length:
            max_command_name_length = len(command_name)
        category = command.category()
        if category not in command_categories:
            command_categories[category] = [command]
        else:
            command_categories[category].append(command)

    command_listing = ''

    for category, category_commands in sorted([(k, v) for (k, v) in command_categories.items()]):
        command_listing += '\n  {}\n\n'.format(category.upper())
        for command in category_commands:
            command_listing += '    {:{}}{}\n'.format(
                command.name(), max_command_name_length + 5, command.short_description())

    parser = argparse.ArgumentParser(
        description='Judge your code',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""available commands:
{}

Use '{} help <command>' to get help for a specific command.""".format(
            command_listing, os.path.basename(sys.argv[0])))
    parser.add_argument('command', help='see below')
    parser.add_argument('args', nargs=argparse.REMAINDER)
    parameters = parser.parse_args(args[1:])

    if parameters.command == 'help':
        if len(parameters.args) == 0:
            parser.print_help()
            return 0
        if len(parameters.args) >= 1 and parameters.args[0] in commands:
            commands[parameters.args[0]].show_help()
            return 0

    if parameters.command not in commands:
        print('\'{}\' is not a valid command. See \'{} help\'.'.format(
            parameters.command, os.path.basename(sys.argv[0])))
        return 1

    return execute(parameters.command, parameters.args)
