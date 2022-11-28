import argparse
import winshell
import os


def create_shortcut(name, target, path):
    print("Creating shortcut for {} at {}".format(target, path))
    with winshell.shortcut(os.path.join(path, name)) as link:
        link.path = target
        link.description = "Start fundbook"


def main():
    parser = argparse.ArgumentParser(description="Create a shortcut")
    parser.add_argument("name", help="Name of the shortcut")
    parser.add_argument("target", help="Target of the shortcut")
    parser.add_argument(
        "path", help="Path to the parent directory of the shortcut file"
    )
    args = parser.parse_args()
    create_shortcut(args.name, os.path.abspath(args.target), os.path.abspath(args.path))


if __name__ == "__main__":
    main()
