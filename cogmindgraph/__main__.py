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

try:
    from .gen import archived_scoresheet_pb2 as scoresheet
except ImportError:
    scoresheet = None

from . import graphs


XAXES = {
    "time": (lambda data: data.cumulative("time"),
             "cumulative playing time (h)"),
    "turns": (lambda data: data.cumulative("turns"),
              "cumulative turns taken"),
    "actions": (lambda data: data.cumulative("actions"),
                "cumulative actions taken"),
    "runs": (lambda data: data.count(), "run count"),
    "date": (lambda data: data["date"], "date"),
}

LOSS_ENDINGS = {
    "CORE DESTROYED": "",
    "SYSTEM CORRUPTED": "C",
    "CRUSHED BY SINGULARITY!": "!",
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
        values = self.select(*args, **kwargs)
        values = (x if np.isfinite(x) else 0 for x in values)
        result = itertools.accumulate(values)
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


def parse_filename(filename):
    parts = re.search(r"(.*)-(\d\d)(\d\d)(\d\d)-(\d\d)(\d\d)(\d\d)"
                      r"(?:-\d)?--?\d+(?:_w\d*)?(\++)?\.txt$", filename)
    player = parts[1].replace("/", "").replace(".", "")
    extended = parts[8]

    date = np.datetime64("20{}-{}-{}T{}:{}:{}"
                         .format(*parts.groups()[1:7]))

    return player, extended, date


def parse_game_legacy(path, args):
    try:
        player, extended, date = parse_filename(path.name)
    except ValueError as e:
        print(f"Warning: {path.name}: {e}")
        return

    if "player" in args and player not in args.player:
        return

    with open(path) as game_file:
        game = game_file.read()

    return player, parse_fields(game, date, extended)


def parse_game_pb(path, args):
    game = scoresheet.ArchivedPostScoresheetRequest()

    with open(path, "rb") as game_file:
        game.ParseFromString(game_file.read())

    sheet = game.scoresheet
    stats = sheet.stats
    player = sheet.header.player_name
    _, extended, date = parse_filename(sheet.header.filename)

    if "player" in args and player not in args.player:
        return

    if not sheet.stats.exploration.spaces_moved.average_speed:
        return

    win, ending = parse_ending(sheet.header.run_result.upper(),
                               sheet.game.win_type)

    time = sum(int(x) * 60**(-i)
               for i, x in enumerate(sheet.game.run_time.split(":")))

    fields = {
        "date": date,
        "extended": extended,
        "win": win,
        "ending": ending,
        "version": re.match(r"(\w+ \d+).*", sheet.header.version)[1],
        "easy": sheet.header.difficulty,
        "score": sheet.performance.total_score,
        "value": sheet.performance.value_destroyed.points,
        "time": time,
        "turns": stats.exploration.turns_passed,
        "actions": stats.actions.total.overall,
        "lore": sheet.game.lore_percent,
        "gallery": sheet.game.gallery_percent,
        "achievements": sheet.game.achievement_percent,
        "speed": 100*100 / stats.exploration.spaces_moved.average_speed,
        "regions": sheet.performance.regions_visited.count,
        "prototypes": sheet.performance.prototypes_identified.count,
        "parts": sheet.peak_state.rating,
        "slots": stats.build.average_slot_usage_percent.overall,
        "damage": stats.combat.damage_inflicted.overall,
        "melee": stats.combat.damage_inflicted.melee,
        "em": stats.combat.damage_inflicted.electromagnetic,
        "core": stats.combat.core_remaining_percent,
        "hacking": sheet.best_states.offensive_hacking,
        "capacity": stats.build.largest_inventory_capacity.average_capacity,
        "influence": stats.alert.peak_influence.average_influence,
        "best_group": stats.allies.total_allies.highest_rated_group,
    }

    return player, fields


def parse_games(score_files, args, func=parse_game_legacy):
    for path in score_files:
        result = func(path, args)

        if not result:
            continue

        player, game = result

        if game["time"] > 0 and game["score"] > 750:
            yield player, game


def parse_ending(ending, win_type):
    if ending == "SELF-DESTRUCTED":
        return -1, ""

    if ending in LOSS_ENDINGS:
        return 0, LOSS_ENDINGS[ending]

    if win_type < 0:
        return 0, ""

    if win_type > 0:
        return 1, str(win_type)

    return 1, ""


def parse_fields(game, date, extended):
    def find(pattern, default=np.nan, type=float):
        match = re.search(pattern, game, re.DOTALL)
        if match:
            return type(match[1])

        return default

    win, ending = parse_ending(find(r"---\[ (.*) \]---", type=str),
                               find(r"Win Type: (\d+)", type=int))

    return {
        "date": date,
        "extended": extended,
        "win": win,
        "ending": ending,
        "version": find(r"Cogmind - (\w+ \d+)", type=str),
        "easy": find(r"Easy Mode: (\d+)", 0),
        "score": find(r"\s+TOTAL SCORE: (-?\d+)"),
        "value": find(r"Value Destroyed \((\d+)\)"),
        "time": find(r"Play Time: (\d+) min") / 60,
        "turns": find(r"Turns Passed\s+(\d+)"),
        "actions": find(r"Actions Taken\s+(\d+)"),
        "lore": find(r"Lore%: (\d+)", 0),
        "gallery": find(r"Gallery%: (\d+)", 0),
        "achievements": find(r"Achievement%: (\d+)", 0),
        "speed": find(r"Average Speed \(%\)\s+(\d+)"),
        "regions": find(r"Regions Visited\s+(\d+)"),
        "prototypes": find(r"Prototype IDs \((\d+)\)"),
        "parts": find(r"Peak State.*?\[Rating: (\d+)\]", 0),
        "slots": find(r"Average Slot Usage \(%\)\s+(\d+)"),
        "damage": find(r"Damage Inflicted\s+(\d+)"),
        "melee": find(r"Damage Inflicted.*?Melee\s+(\d+)"),
        "em": find(r"Damage Inflicted.*?Electromagnetic\s+(\d+)"),
        "core": find(r"Average Core Remaining \(%\)\s+(\d+)"),
        "hacking": find(r"Offensive Hacking\s+(\d+)", 0),
        "capacity": find(r"Average Capacity\s+(\d+)"),
        "influence": find(r"Average Influence\s+(\d+)"),
        "best_group": find(r"Highest-Rated Group\s+(\d+)"),
    }


def plot(graph, data, player, output_dir, args):
    def smart_format(value, pos, base=matplotlib.ticker.EngFormatter(sep="")):
        if 0 < value < 1:
            return f"{value:g}"

        return base(value)

    filename, func = graph

    fig, ax = plt.subplots()
    fig.suptitle(f"{player}'s Cogmind progression", fontsize=8)
    ax.set_xlabel(data.xlabel())

    formatter = matplotlib.ticker.FuncFormatter(smart_format)
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

    basename = output_dir / filename
    plt.savefig(basename.with_suffix(".svg"))
    plt.close(fig)

    if args.format == "png":
        dpi = args.size / fig.get_size_inches()[0]

        import cairosvg
        cairosvg.svg2png(url=str(basename.with_suffix(".svg")), dpi=dpi,
                         write_to=str(basename.with_suffix(".png")))


def plot_all(data, player, output_dir, args):
    for graph in graphs.graphs.items():
        plot(graph, data, player, output_dir, args)


def plot_player(x):
    player, games, args = x
    print(f"{player}: {len(games)} games")

    output_dir = args.output / player
    output_dir.mkdir(parents=True, exist_ok=True)

    data = Data(games, args.xaxis)
    plot_all(data, player, output_dir, args)

    if args.html:
        from . import html
        html.write_player_index(player, output_dir, args.format)


def merge_aliases(scores):
    Alias = collections.namedtuple("Alias", "name games")

    def best_name(aliases):
        return max(aliases, key=lambda x: len(x.games)).name

    def merge_games(aliases):
        return sum((x.games for x in aliases), [])

    players = collections.defaultdict(list)
    for player, games in scores.items():
        canonical_name = player.lower().replace(".", "")
        players[canonical_name].append(Alias(player, games))

    return {best_name(x): merge_games(x) for x in players.values()}


def generate_tasks(scores, args):
    def sort_key(item):
        player, games = item
        return -len(games), player.lower()

    for player, games in sorted(scores.items(), key=sort_key):
        yield player, games, args


def main():
    parser = argparse.ArgumentParser(
        prog="cogmindgraph",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("path", type=pathlib.Path,
                        help="Path to Cogmind scores folder")
    parser.add_argument("output", type=pathlib.Path,
                        help="Path to output folder")
    parser.add_argument("--pb-path", type=pathlib.Path,
                        help="Path to additional protobuf scores")
    parser.add_argument("--xaxis", choices=XAXES.keys(), default="time",
                        help="X axis variable")
    parser.add_argument("--player", action="append", default=argparse.SUPPRESS,
                        help="Only plot the specified player")
    parser.add_argument("--format", choices=["svg", "png"], default="svg",
                        help="Output image format")
    parser.add_argument("--size", type=int, default="1280",
                        help="Output image width")
    parser.add_argument("--html", action="store_true",
                        help="Make HTML index files")
    args = parser.parse_args()

    plt.switch_backend("svg")

    if not args.path.is_dir():
        print(f"Error: '{args.path}' is not a directory!")
        return

    score_files = args.path.glob("*-*-*-*.txt")
    score_files = (x for x in score_files if "_log" not in x.name)

    scores = collections.defaultdict(list)

    for player, game in parse_games(score_files, args):
        scores[player].append(game)

    if args.pb_path:
        if not scoresheet:
            print(f"Error: Run ./build_proto.sh in order to use '--pb-path'!")
            return

        if not args.pb_path.is_dir():
            print(f"Error: '{args.pb_path}' is not a directory!")
            return

        for player, game in parse_games(args.pb_path.glob("*"), args,
                                        func=parse_game_pb):
            scores[player].append(game)

    scores = merge_aliases(scores)
    scores = {k: v for k, v in scores.items() if len(v) >= 2}

    if not scores:
        print("Could not find any players with at least 2 games.")
        return

    if len(scores) > 1:
        print(f"Plotting {len(scores)} players")

    if args.html:
        from . import html
        html.write_index(scores, args.output, args.size)

    with multiprocessing.Pool() as pool:
        for _ in pool.imap(plot_player, generate_tasks(scores, args)):
            pass


if __name__ == "__main__":
    main()
