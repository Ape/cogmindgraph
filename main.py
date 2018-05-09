#!/usr/bin/env python3

import argparse
import collections
import itertools
import multiprocessing
import pathlib
import re

import matplotlib.pyplot as plt
import matplotlib.ticker
import numpy as np

import graphs


XAXES = {
    "time": (lambda data: data.cumulative("time"),
             "cumulative playing time (h)"),
    "turns": (lambda data: data.cumulative("turns"),
              "cumulative turns taken"),
    "runs": (lambda data: data.count(), "run count"),
    "date": (lambda data: data["date"], "date"),
}


class Data:
    def __init__(self, items, xaxis):
        self._items = list(sorted(items, key=lambda x: x["date"]))
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


def parse_games(score_files):
    for path in score_files:
        player, game = parse_game(path)

        if game["time"] > 0 and game["score"] > 750:
            yield player, game


def parse_game(path):
    def parse_filename(path):
        parts = re.search(r"(.*)-(\d\d)(\d\d)(\d\d)-(\d\d)(\d\d)(\d\d)"
                          r"(?:-\d)?--?\d+[_\w+]*\.txt$", path.name)
        player = parts[1].replace("/", "").replace(".", "")
        date = np.datetime64("20{}-{}-{}T{}:{}:{}".format(*parts.groups()[1:]))
        return player, date

    def find(pattern, default=np.nan):
        match = re.search(pattern, game, re.DOTALL)
        if match:
            return float(match[1])

        return default

    with open(path) as game_file:
        game = game_file.read()

    player, date = parse_filename(path)

    return player, {
        "date": date,
        "win": find(r"Win Type: (\d+)", -1),
        "easy": find(r"Easy Mode: (\d+)", 0),
        "score": find(r"\s+TOTAL SCORE: (-?\d+)"),
        "time": find(r"Play Time: (\d+) min") / 60,
        "turns": find(r"Turns Passed\s+(\d+)"),
        "lore": find(r"Lore%: (\d+)"),
        "gallery": find(r"Gallery%: (\d+)"),
        "achievements": find(r"Achievement%: (\d+)"),
        "speed": find(r"Average Speed \(%\)\s+(\d+)"),
        "regions": find(r"Regions Visited\s+(\d+)"),
        "prototypes": find(r"Prototype IDs \((\d+)\)"),
        "parts": find(r"Peak State.*?\[Rating: (\d+)\]"),
        "slots": find(r"Average Slot Usage \(%\)\s+(\d+)"),
        "damage": find(r"Damage Inflicted\s+(\d+)"),
        "melee": find(r"Damage Inflicted.*?Melee\s+(\d+)"),
        "em": find(r"Damage Inflicted.*?Electromagnetic\s+(\d+)"),
        "core": find(r"Average Core Remaining \(%\)\s+(\d+)"),
        "hacking": find(r"Offensive Hacking\s+(\d+)"),
        "capacity": find(r"Average Capacity\s+(\d+)"),
        "influence": find(r"Average Influence\s+(\d+)"),
        "best_group": find(r"Highest-Rated Group\s+(\d+)"),
    }


def plot(graph, data, player, output_dir, args):
    filename, func = graph

    fig, ax = plt.subplots()
    fig.suptitle(f"{player}'s Cogmind progression", fontsize=8)
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

    plt.savefig((output_dir / filename).with_suffix(".png"), dpi=args.dpi)
    plt.close(fig)


def plot_all(data, player, output_dir, args):
    for graph in graphs.graphs():
        plot(graph, data, player, output_dir, args)


def plot_player(x):
    player, games, args = x
    print(f"{player}: {len(games)} games")

    output_dir = args.output / player
    output_dir.mkdir(parents=True, exist_ok=True)

    data = Data(games, args.xaxis)
    plot_all(data, player, output_dir, args)

    if args.html:
        import html
        html.write_player_index(player, output_dir)


def generate_tasks(scores, args):
    def sort_key(item):
        player, games = item
        return -len(games), player.lower()

    for player, games in sorted(scores.items(), key=sort_key):
        yield player, games, args


def main(args):
    if not args.path.is_dir():
        print(f"Error: '{args.path}' is not a directory!")
        return

    score_files = args.path.glob("*-*-*-*.txt")
    score_files = (x for x in score_files if "_log" not in x.name)

    scores = collections.defaultdict(list)

    for player, game in parse_games(score_files):
        scores[player].append(game)

    scores = {k: v for k, v in scores.items() if len(v) >= 2}

    if not scores:
        print("Could not find any players with at least 2 games.")
        return

    if len(scores) > 1:
        print(f"Plotting {len(scores)} players")

    if args.html:
        import html
        html.write_index(scores, args.output)

    with multiprocessing.Pool() as pool:
        for _ in pool.imap(plot_player, generate_tasks(scores, args)):
            pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("path", type=pathlib.Path,
                        help="Path to Cogmind scores folder")
    parser.add_argument("output", type=pathlib.Path,
                        help="Path to output folder")
    parser.add_argument("--xaxis", choices=XAXES.keys(), default="time",
                        help="X axis variable")
    parser.add_argument("--dpi", type=float, default=200,
                        help="Resolution for output files")
    parser.add_argument("--html", action="store_true",
                        help="Make HTML index files")
    main(parser.parse_args())
