import argparse
import sys

from dgit_cmd import *

arg_parser = argparse.ArgumentParser(description="A simple reimplement of Git")
arg_sub_parser = arg_parser.add_subparsers(title="Commands", dest="command")
arg_sub_parser.required = True

# init 命令
argsp = arg_sub_parser.add_parser("init", help="Initialize a new empty repository")
argsp.add_argument("path", metavar="directory", nargs="?",
                   default=".", help="create repository in a directory if given otherwise current as default")

# cat-file 命令
argsp = arg_sub_parser.add_parser("cat-file", help="Provide content of repository objects")
argsp.add_argument("type", metavar="type", choices=['blob', 'commit', 'tag', 'tree'],
                   help="create repository in a directory if given otherwise current as default")
argsp.add_argument("object", metavar="object", help="The object to display")

# hash-object命令
argsp = arg_sub_parser.add_parser("hash-object", help="Compute object ID and optionally creates a blob from a file")
argsp.add_argument("-t", metavar="type", dest="type",
                   choices=['blob', 'commit', 'tag', 'tree'], default="blob", help="Specify the type")
argsp.add_argument("-w", dest="write", action="store_true", help="Actually write the object into repository")
argsp.add_argument("path", help="Read object from <file>")

COMMANDS = {
    "init": cmd_init,
    "cat-file": cmd_cat_file,
    "hash-object": cmd_hash_object,
}


def main(argv=sys.argv[1:]):
    args = arg_parser.parse_args(argv)
    COMMANDS.get(args.command)(args)


if __name__ == '__main__':
    # main(["init", "/var/tst"])
    # main(["cat-file", "blob", "e9f535e07ea846654a6e4eb00f67094ec794b44d", ])
    main(["hash-object", "-w", "/var/tst/a.txt"])
