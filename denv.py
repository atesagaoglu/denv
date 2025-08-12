#!/usr/bin/env python3

import os
import sys
import yaml
import datetime
import tempfile
import subprocess

import parser

vars = {}
post_hook = []
pre_hook = []
paths = []
source = []

# default file, can be set with --config
config_file = os.path.expandvars("$XDG_CONFIG_HOME/denv.yaml")

args = None


def debug(msg):
    if args.debug:
        now = datetime.datetime.now()
        print(f"\033[35m[{now.strftime('%H:%M:%S')}]:\033[39m {msg}")


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

            if "post" in selected:
                post = selected["post"]
                post_hook.extend(post)

            if "pre" in selected:
                pre = selected["pre"]
                pre_hook.extend(pre)

            if "source" in selected:
                src = selected["source"]
                source.extend(src)
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


def subshell_zsh():
    debug("using shell zsh")

    original_zdotdir = os.environ.get("ZDOTDIR")
    original_zshrc = (
        "~/.zshrc"
        if original_zdotdir == None
        else os.path.join(original_zdotdir, ".zshrc")
    )

    debug(f"original zdotdir -> {original_zdotdir}")
    debug(f"original zshrc -> {original_zshrc}")

    with tempfile.TemporaryDirectory() as zdotdir:
        zshrc = os.path.join(zdotdir, ".zshrc")

        with open(zshrc, "w+") as file:

            def append(str):
                file.write(f"{str}\n")

            # Temporarily use the original $ZDOTDIR to load the config then use the new one
            append(f"export ZDOTDIR={original_zdotdir}")
            append(f"cd {original_zdotdir}")
            append(f"source ./.zshrc")
            append(f"export ZDOTDIR={zdotdir}")

            append('echo "in env"')

            debug(f"path -> {paths}")
            debug(f"pre -> {pre_hook}")
            debug(f"post -> {post_hook}")
            debug(f"var -> {vars}")
            debug(f"source -> {source}")

        env = os.environ.copy()
        env["ZDOTDIR"] = zdotdir
        subprocess.run([shell], env=env)


def subshell_bash():
    debug("using shell bash")


def subshell_fish():
    debug("using shell fish")


if __name__ == "__main__":

    args = parser.get_args()
    debug(args)

    # shell based rc creating
    shell = os.environ.get("SHELL")

    if shell.endswith("zsh"):
        subshell_zsh()

    elif shell.endswith("bash"):
        subshell_bash()

    # NOTE: Will I really bother?
    elif shell.endswith("fish"):
        subshell_fish()

    else:
        print(f"Unsupported shell {shell}. Use --eval instead.")

    process(args.key)

    # if args.config and os.path.isfile(args.config):
    #     config_file = args.config

    # TODO: This should be completely changed to work under subshell instead of eval
    # MAYBE: Still allow use of eval with a flag
    # process(args.key)
    #
    # if not args.list_deps:
    #     print(f'export PATH={":".join(post_hook)}:$PATH')
    #
    # for key, value in vars.items():
    #     print(f'export {key}="{value}"')
    #
    # for cmd in cmds:
    #     print(cmd)
