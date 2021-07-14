import argparse
import sys

from dgit_repository import repo_create

arg_parser = argparse.ArgumentParser(description="A simple reimplement of Git")
arg_sub_parser = arg_parser.add_subparsers(title="Commands", dest="command")
arg_sub_parser.required = True

argsp = arg_sub_parser.add_parser("init", help="Initialize a new empty repository")
argsp.add_argument("--path", metavar="directory", nargs="?",
                   default=".", help="create repository in a directory if given otherwise current as default")


def cmd_init(args):
    repo_create(args.path)


COMMANDS = {
    "init": cmd_init,
}


def main(argv=sys.argv[1:]):
    args = arg_parser.parse_args(argv)
    COMMANDS.get(args.command)(args)


if __name__ == '__main__':
    main(["init", "--path", "/var/tst"])
