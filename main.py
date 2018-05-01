#!/usr/bin/env python3

import argparse
import inspect
import itertools
import os
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
    "date": (lambda data: data["date"], "date"),
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
    def parse_date(path):
        parts = re.search("^[\w\s]+-(\d\d)(\d\d)(\d\d)-(\d\d)(\d\d)(\d\d)-",
                          path.name)
        return np.datetime64("20{}-{}-{}T{}:{}:{}".format(*parts.groups()))

    def find(pattern, default=None):
        match = re.search(pattern, game, re.DOTALL)
        if match:
            return float(match[1])

        if default is not None:
            return default

        raise ParseError(f"Can not find '{pattern}' in '{path.name}'")

    with open(path) as game_file:
        game = game_file.read()

    return {
        "date": parse_date(path),
        "win": find("Win Type: (\d+)", -1),
        "easy": find("Easy Mode: (\d+)"),
        "score": find("\s+TOTAL SCORE: (-?\d+)"),
        "time": find("Play Time: (\d+) min") / 60,
        "time_sum": find("Play Time:.*?Cumulative: (\d+) min") / 60,
        "turns": find("Turns Passed\s+(\d+)"),
        "lore": find("Lore%: (\d+)"),
        "gallery": find("Gallery%: (\d+)"),
        "achievements": find("Achievement%: (\d+)", 0),
        "speed": find("Average Speed \(%\)\s+(\d+)"),
        "regions": find("Regions Visited\s+(\d+)"),
        "prototypes": find("Prototype IDs \((\d+)\)"),
        "parts": find("Peak State.*?\[Rating: (\d+)\]", 0),
        "slots": find("Average Slot Usage \(%\)\s+(\d+)"),
        "damage": find("Damage Inflicted\s+(\d+)"),
        "melee": find("Damage Inflicted.*?Melee\s+(\d+)"),
        "em": find("Damage Inflicted.*?Electromagnetic\s+(\d+)"),
        "core": find("Average Core Remaining \(%\)\s+(\d+)"),
        "hacking": find("Offensive Hacking\s+(\d+)", 0),
        "capacity": find("Average Capacity\s+(\d+)"),
        "influence": find("Average Influence\s+(\d+)"),
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
    ax.yaxis.set_major_formatter(formatter)

    if np.issubdtype(data.xaxis().dtype, np.datetime64):
        fig.autofmt_xdate()
        margin = 0.2 * (max(data.xaxis()) - min(data.xaxis()))
        ax.set_xlim(min(data.xaxis()) - margin,
                    max(data.xaxis()) + margin)
    else:
        ax.xaxis.set_major_formatter(formatter)

    func(ax, data)

    if np.issubdtype(data.xaxis().dtype, np.datetime64):
        ax.set_xlim(ax.get_xticks()[0], ax.get_xticks()[-1])
    else:
        ax.set_xlim(0, ax.get_xticks()[-1])

    ax.set_ylim(ymax=ax.get_yticks()[-1])

    if "output" in args:
        plt.savefig((args.output / filename).with_suffix(".png"), dpi=args.dpi)


def plot_all(data, args):
    for graph in inspect.getmembers(graphs.Graphs,
                                    predicate=inspect.isfunction):
        plot(graph, data, args)

    if "output" not in args:
        plt.show()


def main(args):
    if not args.path.is_dir():
        print(f"Error: '{args.path}' is not a directory!")
        return

    scores = args.path.glob("*-*-*-*-*.txt")
    scores = (x for x in scores if "_log" not in x.name)
    games = list(sorted(parse_games(scores), key=lambda x: x["date"]))

    if not games:
        print("Could not find any valid score files!")
        return
    elif len(games) == 1:
        print("Found only one score file!")
        print("At least two are required for meaningful graphs.")
        return

    if "output" in args and not args.output.is_dir():
        try:
            os.mkdir(args.output)
        except IOError as e:
            print(f"Error: Failed to create output directory: {e.strerror}")
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
