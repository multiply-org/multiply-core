import sys
import numpy as np
from cate.util.cli import run_main, SubCommandCommand

#: Name of command line executable
CLI_NAME = 'example'
CLI_DESCRIPTION = 'MULTIPLY command line example'

__version__ = '0.1'


class ExampleCommand(SubCommandCommand):

    @classmethod
    def name(cls):
        return 'ex1'

    @classmethod
    def parser_kwargs(cls):
        return dict(help='Provide a first example for a command line interface',
                    description='This is just an example.')

    @classmethod
    def configure_parser_and_subparsers(cls, parser, subparsers):
        list_parser = subparsers.add_parser('list', help='List some things.')
        list_parser.add_argument('--first', '-f', action='store_true', help="List only first half of things.")
        list_parser.add_argument('--contains', '-c', metavar='CONTAINS', help="List only things that include CONTAINS.")
        list_parser.set_defaults(sub_command_function=cls._execute_list)

    @classmethod
    def _execute_list(cls, command_args):
        list_of_things = np.array(['x', '1x', '2x', 'y'])
        count = len(list_of_things)
        if command_args.first:
            count = int(count / 2)
        for i in range(count):
            if command_args.contains:
                if command_args.contains in list_of_things[i]:
                    print(list_of_things[i])
            else:
                print(list_of_things[i])

# list of commands supported by the CLI. Entries are classes derived from :py:class:'Command' class-
COMMAND_REGISTRY = [ExampleCommand]

def main(args=None) -> int:
    # noinspection PyTypeChecker
    return run_main(CLI_NAME,
                    CLI_DESCRIPTION,
                    __version__,
                    COMMAND_REGISTRY,
                    license_text='license text',
                    docs_url='url to docs',
                    error_message_trimmer=None,
                    args=args)

if __name__ == '__main__':
    sys.exit(main())