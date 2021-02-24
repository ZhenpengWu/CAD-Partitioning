import argparse

from app import App

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""TODO"""
    )

    parser.add_argument(
        "-v",
        "--verbose",
        help="enable verbose logging",
        action="store_true",
    )

    parser.add_argument(
        "-g",
        "--no-gui",
        help="""
        disable graphical user interface (GUI), and
        automatically enable if no other arguments specified
        """,
        action="store_true",
    )

    parser.add_argument("-i", "--infile", help="test input file")

    parser.add_argument(
        "-a",
        "--all",
        help="""
        test all benchmarks, and
        GUI is automatically disabled
        """,
        action="store_true",
    )

    args = parser.parse_args()

    App(args)
