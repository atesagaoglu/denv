#!/usr/bin/env python3

import os
import sys
import yaml
import pathlib
import argparse

paths = []
vars = {}
cmds = []

# default file, can be set with --config
config_file = os.path.expandvars("$XDG_CONFIG_HOME/denv.yaml")

args = None


def process(key):

    with open(config_file, "r") as file:
        obj = yaml.load(file, Loader=yaml.SafeLoader)

        # MAYBE: Do this outside and remember keys
        if args.list:
            for k in obj.keys():
                print(f"echo - {k}")
            exit()

        try:
            selected = obj[key]
        except KeyError:
            print(f"Environment {key} not found!")
            exit()

        # Do not set anything if list is set
        if not args.list_deps:

            if "path" in selected:
                path = selected["path"]
                paths.extend(path)

            if "var" in selected:
                var = selected["var"]
                vars.update(var)

            if "cmd" in selected:
                cmd = selected["cmd"]
                cmds.extend(cmd)
        else:
            print(f'echo "Dependencies:"')

        # Recursively call dependencies
        if (not args.no_deps) and "dep" in selected:
            dep = selected["dep"]
            for d in dep:
                if args.list_deps:
                    print(f"echo - {d}")
                    continue
                process(d)


if __name__ == "__main__":

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

    args = parser.parse_args()

    # key can only be None when list is set
    if not args.list and not args.key:
        parser.print_help()

    if args.config and os.path.isfile(args.config):
        config_file = args.config

    process(args.key)

    if not args.list_deps:
        print(f'export PATH={":".join(paths)}:$PATH')

    for key, value in vars.items():
        print(f'export {key}="{value}"')

    for cmd in cmds:
        # eval will call these
        print(cmd)
