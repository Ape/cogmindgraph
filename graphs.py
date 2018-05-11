import math

import matplotlib.dates
import matplotlib.ticker
import numpy as np


graphs = {}


def graph(func):
    graphs[func.__name__] = func
    return func


def scatter_plot(ax, data, y, ymin=0, mark_versions=True):
    x = data.xaxis()
    win = data["win"] >= 0
    normal = data["easy"] == 0
    easy = data["easy"] == 1
    easiest = data["easy"] == 2

    extended = np.nonzero(data["extended"])
    extended2 = data["extended"] == "++"
    ax.scatter(x[extended], y[extended], s=80, color="k", facecolors="none",
               linewidths=0.5)
    ax.scatter(x[extended2], y[extended2], s=120, color="k", facecolors="none",
               linewidths=0.5)

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

    trendline(ax, data, y)

    if mark_versions:
        version_markers(ax, data)

    if win.any() or easy.any() or easiest.any():
        legend(ax)


def legend(ax):
    ax.legend(loc="upper right", bbox_to_anchor=(1, 1),
              bbox_transform=ax.get_figure().transFigure,
              borderaxespad=0.1, prop={"size": 8})


def trendline(ax, data, y):
    x = ordinal(data.xaxis())

    trend_locs = [0, ax.get_xticks()[-1]]
    valid = np.isfinite(y)

    if np.count_nonzero(valid) < 2:
        return

    trend = np.poly1d(np.polyfit(x[valid], y[valid], 1))
    ax.autoscale(False)
    ax.plot(trend_locs, trend(trend_locs), "--", color="0.5", zorder=0)


def version_markers(ax, data):
    def label(version, position, xycoords="data"):
        ax.annotate(version.lower(), position, xycoords=xycoords,
                    xytext=(-0.5, -4.5), textcoords="offset points",
                    size=5, rotation=-90, zorder=0)

    def changed_values(y):
        return np.where(y[:-1] != y[1:])[0] + 1

    x = ordinal(data.xaxis())
    y = data["version"]
    label(y[0], (0, 1), xycoords="axes fraction")

    for i in changed_values(y):
        ax.axvline(x[i], linewidth=0.5, color="0.5", zorder=0)
        label(y[i], (x[i], ax.get_yticks()[-1]))


def divide_safe(a, b):
    return np.divide(a, b, out=np.zeros(a.shape), where=b != 0)


def ordinal(x):
    if np.issubdtype(x.dtype, np.datetime64):
        x = matplotlib.dates.date2num(x)

    return x


@graph
def completion(ax, data):
    x = data.xaxis()
    ax.plot(x, data["lore"], label="lore")

    # Skip color #2 because we have used it to mean 'win'
    next(ax._get_lines.prop_cycler)

    ax.plot(x, data["achievements"], label="achievements")
    ax.plot(x, data["gallery"], label="gallery")
    ax.set_ylim(0, 100)
    legend(ax)
    ax.set_ylabel("completion percentage")
    ax.set_title("Completion")
    version_markers(ax, data)


@graph
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
    version_markers(ax, data)

    if easy(data).any() or easiest(data).any():
        legend(ax)


@graph
def score(ax, data):
    scatter_plot(ax, data, data["score"])
    ax.set_ylabel("score")
    ax.set_title("Score")


@graph
def value(ax, data):
    scatter_plot(ax, data, data["value"])
    ax.set_ylabel("value")
    ax.set_title("Value destroyed")


@graph
def time(ax, data):
    scatter_plot(ax, data, data["time"])
    ax.set_ylabel("game length (h)")
    ax.set_title("Game length")


@graph
def turns(ax, data):
    scatter_plot(ax, data, data["turns"])
    ax.set_ylabel("turns")
    ax.set_title("Game length (turns taken)")


@graph
def actions(ax, data):
    scatter_plot(ax, data, data["actions"])
    ax.set_ylabel("actions")
    ax.set_title("Game length (actions taken)")


@graph
def tempo(ax, data):
    scatter_plot(ax, data, data["actions"] / (60 * data["time"]))
    ax.set_ylabel("actions per minute")
    ax.set_title("Playing tempo")


@graph
def speed(ax, data):
    scatter_plot(ax, data, data["speed"])
    ax.set_ylabel("average speed (%)")
    ax.set_title("Movement speed")


@graph
def regions(ax, data):
    scatter_plot(ax, data, data["regions"])
    ax.set_ylabel("regions")
    ax.set_title("Regions visited")


@graph
def prototypes(ax, data):
    scatter_plot(ax, data, data["prototypes"])
    ax.set_ylabel("prototype IDs")
    ax.set_title("Prototype IDs")


@graph
def parts(ax, data):
    scatter_plot(ax, data, data["parts"])
    ax.set_ylabel("peak state rating")
    ax.set_title("Part rating")


@graph
def slots(ax, data):
    ax.set_ylim(ymax=100)
    scatter_plot(ax, data, data["slots"])
    ax.set_ylabel("average slot usage (%)")
    ax.set_title("Slot usage")


@graph
def damage(ax, data):
    scatter_plot(ax, data, 100 * data["damage"] / data["turns"])
    ax.set_ylabel("damage inflicted per 100 turns")
    ax.set_title("Damage rate")


@graph
def melee(ax, data):
    y = 100 * divide_safe(data["melee"], data["damage"])
    ax.set_ylim(ymax=100)
    scatter_plot(ax, data, y)
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter())
    ax.set_ylabel("melee damage")
    ax.set_title("Melee")


@graph
def em(ax, data):
    y = 100 * divide_safe(data["em"], data["damage"])
    ax.set_ylim(ymax=100)
    scatter_plot(ax, data, y)
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter())
    ax.set_ylabel("EM damage")
    ax.set_title("Electromagnetic damage")


@graph
def core(ax, data):
    ax.set_ylim(ymax=100)
    scatter_plot(ax, data, data["core"])
    ax.set_ylabel("average core remaining (%)")
    ax.set_title("Core integrity")


@graph
def hacking(ax, data):
    scatter_plot(ax, data, data["hacking"])
    ax.set_ylabel("peak offensive hacking")
    ax.set_title("Hacking")


@graph
def capacity(ax, data):
    scatter_plot(ax, data, data["capacity"])
    ax.set_ylabel("average capacity")
    ax.set_title("Inventory capacity")
    locator = matplotlib.ticker.MaxNLocator(integer=True,
                                            steps=[1, 2, 5, 10])
    ax.yaxis.set_major_locator(locator)


@graph
def influence(ax, data):
    tick = math.log(200, 2)
    cutoff = tick - 6

    y = data["influence"]
    y = np.log2(y.clip(2**cutoff))
    scatter_plot(ax, data, y, ymin=None, mark_versions=False)
    ax.set_ylabel("average influence")
    ax.set_title("Influence")

    tick_start = math.floor(min(y) - tick)
    tick_stop = math.ceil(max(y) - tick) + 1
    ax.set_yticks([tick + x for x in range(tick_start, tick_stop)])
    version_markers(ax, data)

    if min(y) <= cutoff:
        ax.set_ylim(ymin=cutoff)

    def format_func(value, *args):
        if value <= cutoff:
            return 0

        return f"{2**value:g}"

    formatter = matplotlib.ticker.FuncFormatter(format_func)
    ax.yaxis.set_major_formatter(formatter)


@graph
def best_group(ax, data):
    scatter_plot(ax, data, data["best_group"])
    ax.set_ylabel("highest-rated group")
    ax.set_title("Ally group rating")
