#!/usr/bin/env python3

import argparse
import inspect
import itertools
import pathlib
import re

import matplotlib.pyplot as plt
import matplotlib.ticker
import numpy as np

import graphs


XAXES = {
    "time": (lambda data: data["time_sum"], "cumulative playing time (h)"),
    "turns": (lambda data: data.cumulative("turns"), "cumulative turns taken"),
    "runs": (lambda data: data.count(), "run count"),
}


class Data:
    def __init__(self, items, xaxis):
        self._items = items
        self._xaxis = xaxis

    def select(self, field, where=lambda x: True):
        return (x[field] for x in self._items if where(x))

    def __getitem__(self, field):
        return self._to_array(self.select(field))

    def array(self, *args, **kwargs):
        return self._to_array(self.select(*args, **kwargs))

    def cumulative(self, *args, **kwargs):
        result = itertools.accumulate(self.select(*args, **kwargs))
        return self._to_array(result)

    def max(self, *args, **kwargs):
        result = itertools.accumulate(self.select(*args, **kwargs), max)
        return self._to_array(result)

    def count(self):
        return self._to_array(range(1, len(self._items) + 1))

    def xaxis(self):
        return XAXES[self._xaxis][0](self)

    def xlabel(self):
        return XAXES[self._xaxis][1]

    def _to_array(self, generator):
        return np.array(list(generator))


def sort_scores(filename):
    parts = filename.name.split("-")
    return parts[1], parts[2]


def parse_games(scores):
    for path in scores:
        try:
            game = parse_game(path)
        except ParseError as e:
            print(f"Warning: {e}")
            continue

        if game["time"] > 0 and game["score"] > 750:
            yield game


class ParseError(Exception):
    pass


def parse_game(path):
    with open(path) as game_file:
        game = game_file.read()

    def find(pattern, default=None):
        match = re.search(pattern, game)
        if match:
            return int(match[1])

        if default is not None:
            return default

        raise ParseError(f"Can not find '{pattern}' in '{path.name}'")

    return {
        "win": find("Win Type: (\d+)", -1),
        "easy": find("Easy Mode: (\d+)"),
        "score": find("\s+TOTAL SCORE: (-?\d+)"),
        "time": find("Play Time: (\d+) min") / 60,
        "time_sum": find("Cumulative: (\d+) min") / 60,
        "turns": find("Turns Passed\s+(\d+)"),
        "lore": find("Lore%: (\d+)"),
        "speed": find("Average Speed \(%\)\s+(\d+)"),
        "prototypes": find("Prototype IDs \((\d+)\)"),
        "parts": find("\[Rating: (\d+)\]", 0),
        "damage": find("Damage Inflicted\s+(\d+)"),
        "capacity": find("Average Capacity\s+(\d+)"),
        "best_group": find("Highest-Rated Group\s+(\d+)"),
    }


def plot(graph, data, args):
    filename, func = graph

    def name_text():
        if "name" in args:
            return f"{args.name}'s "

        return ""

    fig, ax = plt.subplots()
    fig.suptitle(f"{name_text()}Cogmind progression", fontsize=8)
    ax.set_xlabel(data.xlabel())

    formatter = matplotlib.ticker.EngFormatter(sep="")
    ax.xaxis.set_major_formatter(formatter)
    ax.yaxis.set_major_formatter(formatter)

    func(ax, data)

    ax.set_xlim(0, ax.get_xticks()[-1])
    ax.set_ylim(0, ax.get_yticks()[-1])

    if "output" in args:
        plt.savefig((args.output / filename).with_suffix(".png"), dpi=args.dpi)


def plot_all(data, args):
    for graph in inspect.getmembers(graphs.Graphs,
                                    predicate=inspect.isfunction):
        plot(graph, data, args)

    if "output" not in args:
        plt.show()


def main(args):
    scores = sorted(args.path.glob("*-*-*-*-*.txt"), key=sort_scores)
    scores = (x for x in scores if "_log" not in x.name)
    games = list(parse_games(scores))

    if not games:
        print("Could not find any valid score files!")
        return

    data = Data(games, args.xaxis)
    plot_all(data, args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("path", type=pathlib.Path,
                        help="Path to Cogmind scores folder")
    parser.add_argument("--xaxis", choices=XAXES.keys(), default="time",
                        help="X axis variable")
    parser.add_argument("--name", default=argparse.SUPPRESS,
                        help="Player name")
    parser.add_argument("--output", type=pathlib.Path,
                        default=argparse.SUPPRESS,
                        help="Path to output folder")
    parser.add_argument("--dpi", type=float, default=200,
                        help="Resolution for output files")
    main(parser.parse_args())
