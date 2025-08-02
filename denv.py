#!/usr/bin/env python3

import os
import sys
import yaml
import pathlib
import argparse
import subprocess

paths = []
vars = {}
cmds = []

# default file, can be set with --config
config_file = os.path.expandvars("$XDG_CONFIG_HOME/denv.yaml")


def process(key):

    with open(config_file, "r") as file:
        obj = yaml.load(file, Loader=yaml.SafeLoader)

        try:
            selected = obj[key]
        except KeyError:
            print(f"Environment {key} not found!")
            exit()

        if "path" in selected:
            path = selected["path"]
            paths.extend(path)

        if "var" in selected:
            var = selected["var"]
            vars.update(var)

        # Recursively call dependencies
        if "dep" in selected:
            dep = selected["dep"]
            for d in dep:
                process(d)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        prog="denv",
        description="Setup dev environments from yaml files.",
        usage="denv.py <env_name> [options]",
        add_help=False,
    )
    parser.error = lambda msg: print(msg) or parser.print_help() or exit(1)

    parser.add_argument("key", help="Dev environement to setup from the file.")
    parser.add_argument(
        "-c", "--config", help="Specify a config file to use.", type=pathlib.Path
    )
    parser.add_argument(
        "-h", "--help", action="help", help="Displays the help message."
    )

    args = parser.parse_args()

    if args.config and os.path.isfile(args.config):
        config_file = args.config

    process(args.key)

    print(f'export PATH={":".join(paths)}:$PATH')

    for key, value in vars.items():
        print(f'export {key}="{value}"')
