from cate.util.cli import run_main, SubCommandCommand

#: Name of Command line executable
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

def main(args=None) -> int:
    # noinspection PyTypeChecker
    return run_main(CLI_NAME,
                    CLI_DESCRIPTION,
                    __version__,
                    COMMAND_REGISTRY,
                    license_text=_LICENSE,
                    docs_url=_DOCS_URL,
                    error_message_trimmer=_trim_error_message,
                    args=args)


if __name__ == '__main__':
    sys.exit(main())