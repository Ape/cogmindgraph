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


class Data:
    def __init__(self, items, turns_xaxis):
        self.items = list(items)
        self.turns_xaxis = turns_xaxis

    def select(self, field):
        return (x[field] for x in self.items)

    def __getitem__(self, field):
        return self._to_array(self.select(field))

    def cumulative(self, field):
        return self._to_array(itertools.accumulate(self.select(field)))

    def max(self, field):
        return self._to_array(itertools.accumulate(self.select(field), max))

    def xaxis(self):
        if self.turns_xaxis:
            return self.cumulative("turns")

        return self["time_sum"]

    def xlabel(self):
        if self.turns_xaxis:
            return "cumulative turns taken"

        return "cumulative playing time (h)"

    def _to_array(self, generator):
        return np.array(list(generator))


def parse_game(path):
    with open(path) as game_file:
        game = game_file.read()

    def find(pattern):
        return int(re.search(pattern, game)[1])

    def matches(pattern):
        match = re.search(pattern, game)
        if match:
            return int(match[1])

        return None

    return {
        "win": matches("Win Type: (\d+)"),
        "score": find("\s+TOTAL SCORE: (\d+)"),
        "time": find("Play Time: (\d+) min") / 60,
        "time_sum": find("Cumulative: (\d+) min") / 60,
        "turns": find("Turns Passed\s+(\d+)"),
        "lore": find("Lore%: (\d+)"),
        "speed": find("Average Speed \(%\)\s+(\d+)"),
        "prototypes": find("Prototype IDs \((\d+)\)"),
        "parts": find("\[Rating: (\d+)\]"),
        "damage": find("Damage Inflicted\s+(\d+)"),
        "capacity": find("Average Capacity\s+(\d+)"),
        "best_group": find("Highest-Rated Group\s+(\d+)"),
    }


def plot(graph, data, args):
    filename, func = graph

    def name_text():
        if args.name:
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

    if args.output:
        plt.savefig((args.output / filename).with_suffix(".png"), dpi=args.dpi)


def plot_all(data, args):
    for graph in inspect.getmembers(graphs.Graphs,
                                    predicate=inspect.isfunction):
        plot(graph, data, args)

    if not args.output:
        plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=pathlib.Path,
                        help="Path to Cogmind folder")
    parser.add_argument("--turns", action="store_true",
                        help="Use turns as the X axis instead of playing time")
    parser.add_argument("--name",
                        help="Player name")
    parser.add_argument("--output", type=pathlib.Path,
                        help="Path to output folder")
    parser.add_argument("--dpi", type=float, default=200,
                        help="Resolution for output files")
    args = parser.parse_args()

    scores = sorted((args.path / "scores").iterdir())
    data = Data((parse_game(x) for x in scores), args.turns)
    plot_all(data, args)
