#!/usr/bin/env python3

import os
import yaml
import sys
import subprocess

paths = []
vars = {}
cmds = []

def process(key):
    # assumes file exists
    config_file = os.path.expandvars("$XDG_CONFIG_HOME/denv.yaml")

    with open(config_file, "r") as file:
        obj = yaml.load(file, Loader=yaml.SafeLoader)

        try:
            selected = obj[key]
        except KeyError:
            print(f'Environment {key} not found!')
            exit()

        if "path" in selected:
            path = selected["path"]
            paths.extend(path)

        # Recursively call dependencies
        if "dep" in selected:
            dep = selected["dep"]
            for d in dep:
                process(d)

if __name__ == "__main__":
    process(sys.argv[1])

    print(f'export PATH={":".join(paths)}:$PATH')
