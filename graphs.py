import inspect
import math

import matplotlib.dates
import matplotlib.ticker
import numpy as np


def scatter_plot(ax, data, y, ymin=0, legend_loc="upper left"):
    x = data.xaxis()
    win = data["win"] >= 0
    normal = data["easy"] == 0
    easy = data["easy"] == 1
    easiest = data["easy"] == 2

    ax.scatter(x[~win & normal], y[~win & normal], color="C0")

    if win.any():
        ax.scatter(x[win & normal], y[win & normal], color="C1", label="win")

    if easy.any():
        ax.scatter(x[~win & easy], y[~win & easy], color="C0",
                   facecolors="none", label="easy")
        ax.scatter(x[win & easy], y[win & easy], color="C1", facecolors="w")

    if easiest.any():
        ax.scatter(x[~win & easiest], y[~win & easiest], color="C0",
                   facecolors="none", linestyle=":", label="easiest")
        ax.scatter(x[win & easiest], y[win & easiest], color="C1",
                   facecolors="w", linestyle=":")

    ax.set_ylim(ymin=ymin)

    for i, win_type in enumerate(data["win"]):
        if win_type > 0:
            ax.annotate(int(win_type), (x[i], y[i]), size=6, weight="bold",
                        xytext=(-2, -2.25), textcoords="offset points")

    trendline(ax, x, y)

    if win.any() or easy.any() or easiest.any():
        ax.legend(loc=legend_loc, prop={"size": 8})


def trendline(ax, x, y):
    if np.issubdtype(x.dtype, np.datetime64):
        x = matplotlib.dates.date2num(x)

    trend_locs = [0, ax.get_xticks()[-1]]
    trend = np.poly1d(np.polyfit(x, y, 1))
    ax.autoscale(False)
    ax.plot(trend_locs, trend(trend_locs), "--", color="0.5", zorder=0)


def divide_safe(a, b):
    return np.divide(a, b, out=np.zeros(a.shape), where=b != 0)


def graphs():
    return inspect.getmembers(Graphs, predicate=inspect.isfunction)


class Graphs:
    def completion(ax, data):
        x = data.xaxis()
        ax.plot(x, data["lore"], label="lore")

        # Skip color #2 because we have used it to mean 'win'
        next(ax._get_lines.prop_cycler)

        ax.plot(x, data["achievements"], label="achievements")
        ax.plot(x, data["gallery"], label="gallery")
        ax.set_ylim(0, 100)
        ax.legend(loc="upper left", prop={"size": 8})
        ax.set_ylabel("completion percentage")
        ax.set_title("Completion")

    def high_score(ax, data):
        def normal(item):
            return item["easy"] == 0

        def easy(item):
            return item["easy"] == 1

        def easiest(item):
            return item["easy"] == 2

        x = data.xaxis()
        ax.plot(x[normal(data)], data.max("score", where=normal),
                label="normal")
        ax.plot(x[easy(data)], data.max("score", where=easy), color="C0",
                linestyle="--", label="easy")
        ax.plot(x[easiest(data)], data.max("score", where=easiest), color="C0",
                linestyle=":", label="easiest")
        ax.set_ylim(ymin=0)
        ax.set_ylabel("score")
        ax.set_title("High score")

        if easy(data).any() or easiest(data).any():
            ax.legend(loc="upper left", prop={"size": 8})

    def score(ax, data):
        scatter_plot(ax, data, data["score"])
        ax.set_ylabel("score")
        ax.set_title("Score")

    def time(ax, data):
        scatter_plot(ax, data, data["time"])
        ax.set_ylabel("game length (h)")
        ax.set_title("Game length")

    def turns(ax, data):
        scatter_plot(ax, data, data["turns"])
        ax.set_ylabel("turns")
        ax.set_title("Game length (turns taken)")

    def tempo(ax, data):
        scatter_plot(ax, data, data["turns"] / (60 * data["time"]))
        ax.set_ylabel("turns per minute")
        ax.set_title("Playing tempo")

    def speed(ax, data):
        scatter_plot(ax, data, data["speed"])
        ax.set_ylabel("average speed (%)")
        ax.set_title("Movement speed")

    def regions(ax, data):
        scatter_plot(ax, data, data["regions"])
        ax.set_ylabel("regions")
        ax.set_title("Regions visited")

    def prototypes(ax, data):
        scatter_plot(ax, data, data["prototypes"])
        ax.set_ylabel("prototype IDs")
        ax.set_title("Prototype IDs")

    def parts(ax, data):
        scatter_plot(ax, data, data["parts"])
        ax.set_ylabel("peak state rating")
        ax.set_title("Part rating")

    def slots(ax, data):
        scatter_plot(ax, data, data["slots"], legend_loc="lower left")
        ax.set_ylim(ymax=100)
        ax.set_ylabel("average slot usage (%)")
        ax.set_title("Slot usage")

    def damage(ax, data):
        scatter_plot(ax, data, 100 * data["damage"] / data["turns"])
        ax.set_ylabel("damage inflicted per 100 turns")
        ax.set_title("Damage rate")

    def melee(ax, data):
        y = 100 * divide_safe(data["melee"], data["damage"])
        scatter_plot(ax, data, y)
        ax.set_ylim(ymax=100)
        ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter())
        ax.set_ylabel("melee damage")
        ax.set_title("Melee")

    def em(ax, data):
        y = 100 * divide_safe(data["em"], data["damage"])
        scatter_plot(ax, data, y)
        ax.set_ylim(ymax=100)
        ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter())
        ax.set_ylabel("EM damage")
        ax.set_title("Electromagnetic damage")

    def core(ax, data):
        scatter_plot(ax, data, data["core"], legend_loc="lower left")
        ax.set_ylim(ymax=100)
        ax.set_ylabel("average core remaining (%)")
        ax.set_title("Core integrity")

    def hacking(ax, data):
        scatter_plot(ax, data, data["hacking"])
        ax.set_ylabel("peak offensive hacking")
        ax.set_title("Hacking")

    def capacity(ax, data):
        scatter_plot(ax, data, data["capacity"])
        ax.set_ylabel("average capacity")
        ax.set_title("Inventory capacity")
        locator = matplotlib.ticker.MaxNLocator(integer=True,
                                                steps=[1, 2, 5, 10])
        ax.yaxis.set_major_locator(locator)

    def influence(ax, data):
        tick = math.log(200, 2)
        cutoff = tick - 6

        y = data["influence"]
        y = np.log2(y.clip(2**cutoff))
        scatter_plot(ax, data, y, ymin=None)
        ax.set_ylabel("average influence")
        ax.set_title("Influence")

        tick_start = math.floor(min(y) - tick)
        tick_stop = math.ceil(max(y) - tick) + 1
        ax.set_yticks([tick + x for x in range(tick_start, tick_stop)])

        if min(y) <= cutoff:
            ax.set_ylim(ymin=cutoff)

        def format_func(value, *args):
            if value <= cutoff:
                return 0

            return f"{2**value:g}"

        formatter = matplotlib.ticker.FuncFormatter(format_func)
        ax.yaxis.set_major_formatter(formatter)

    def best_group(ax, data):
        scatter_plot(ax, data, data["best_group"])
        ax.set_ylabel("highest-rated group")
        ax.set_title("Ally group rating")
