#!/usr/bin/env python3

import os
import sys
import yaml
import datetime
import tempfile
import subprocess
import time

import parser

vars = {}
post_hook = []
pre_hook = []
paths = []
source = []
cwd = None

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

            if "cwd" in selected:
                global cwd
                cwd = selected["cwd"]

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
    original_zdotdir = os.environ.get("ZDOTDIR")
    if original_zdotdir is None:
        original_zdotdir = os.path.expanduser("~")

    cwd = os.getcwd()

    with tempfile.TemporaryDirectory() as zdotdir:
        with open(os.path.join(zdotdir, ".zshrc"), "w+") as file:

            def append(str):
                file.write(f"{str}\n")

            # Temporarily use the original $ZDOTDIR to load the config then use the new one
            append(f"export ZDOTDIR={original_zdotdir}")
            append(f"cd {original_zdotdir}")
            append(f"source ./.zshrc")
            append(f"export ZDOTDIR={zdotdir}")
            append(f"cd {cwd}")

            # remove duplicates
            append("typeset -U path")
            append('path=("${(@s/:/)PATH}")')
            append('PATH="${(j/:/)path}"')

            write_to_rc(append)

            file.flush()

            env = os.environ.copy()
            env["ZDOTDIR"] = zdotdir
            env["DENV_ACTIVE_ENV"] = args.key
            subprocess.run([shell], env=env)


def subshell_bash():

    original_bashrc = os.path.expandvars("$HOME/.bashrc")

    with tempfile.NamedTemporaryFile("w") as file:

        def append(str):
            file.write(f"{str}\n")

        append(f"source {original_bashrc}")

        append("export PATH=$(awk -v RS=: -v ORS=: '!a[$1]++' <<< \"$PATH\")")
        append("PATH=${PATH%:}")

        write_to_rc(append)

        file.flush()

        env = os.environ.copy()
        env["DENV_ACTIVE_ENV"] = args.key
        subprocess.run([shell, "--rcfile", file.name], env=env)


def subshell_fish():
    print(
        "I probably won't implement fish support anytime soon.",
        "Please use a proper shell.",
    )


def write_to_rc(append):
    for s in source:
        append(f'source "{s}"')

    for p in pre_hook:
        append(pre_hook)

    for p in paths:
        append(f'export PATH="{p}:$PATH"')

    for k, v in vars.items():
        append(f'export {k}="{v}"')

    for p in post_hook:
        append(p)

    expanded_cwd = os.path.expandvars(cwd)
    if cwd and not os.path.exists(expanded_cwd):
        os.mkdir(expanded_cwd)
    append(f'cd "{expanded_cwd}"')


# TODO: YAML format validation is necessary to avoid unexpected behavior
if __name__ == "__main__":

    if os.name == "nt":
        print("Windows not supported.")
        print("Please use a real operating system.")
        time.sleep(3)
        os.startfile(
            "https://medium.com/@kc_clintone/installing-linux-a-step-by-step-guide-77471a47322d"
        )
        exit(-1)

    args = parser.get_args()
    debug(args)

    # shell based rc creating
    shell = os.environ.get("SHELL")

    if not shell:
        print("Couldn't find shell")
        exit(-1)

    process(args.key)

    if shell.endswith("zsh"):
        subshell_zsh()

    elif shell.endswith("bash"):
        subshell_bash()

    # NOTE: Will I really bother?
    elif shell.endswith("fish"):
        subshell_fish()

    else:
        print(f"Unsupported shell {shell}. Use --eval instead.")
