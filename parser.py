import argparse
import pathlib


def get_args():
    # MAYBE: Parser rules should be defined in another file
    parser = argparse.ArgumentParser(
        prog="denv",
        description="Setup dev environments from yaml files.",
        usage="denv.py <env_name> [options]",
        add_help=False,
    )
    parser.error = lambda msg: print(msg) or parser.print_help() or exit(1)

    parser.add_argument(
        "key", help="Dev environement to setup from the file.", nargs="?", default=None
    )
    parser.add_argument(
        "--no-deps",
        "-n",
        help="Setup an environement without setting up it's dependencies",
        action="store_true",
    )
    parser.add_argument(
        "--list", "-l", help="Lists defined environments.", action="store_true"
    )
    parser.add_argument(
        "--list-deps",
        "-L",
        help="Lists dependencies of an environment.",
        action="store_true",
    )
    parser.add_argument(
        "-c", "--config", help="Specify a config file to use.", type=pathlib.Path
    )
    parser.add_argument(
        "-h", "--help", action="help", help="Displays the help message."
    )
    parser.add_argument(
        "--debug",
        help="Run in debug mode. Prints debug statements.",
        action="store_true",
    )

    args = parser.parse_args()

    # key can only be None when list is set
    if not args.list and not args.key:
        parser.print_help()

    return args
