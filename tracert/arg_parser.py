from argparse import ArgumentParser


def arg_parse():
    parser = ArgumentParser()
    parser.add_argument("destination", type=str, nargs="*", default="e1.ru")
    args = parser.parse_args()
    return args.destination
