import matplotlib.ticker
import numpy as np


def scatter_plot(ax, data, y):
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

    for i, win_type in enumerate(data["win"]):
        if win_type > 0:
            ax.annotate(win_type, (x[i], y[i]), size=6, weight="bold",
                        xytext=(-2, -2.25), textcoords="offset points")

    trendline(ax, x, y)

    if win.any() or easy.any() or easiest.any():
        ax.legend(loc="upper left", prop={"size": 8})


def trendline(ax, x, y):
    trend_locs = [0, ax.get_xticks()[-1]]
    trend = np.poly1d(np.polyfit(x, y, 1))
    ax.autoscale(False)
    ax.plot(trend_locs, trend(trend_locs), "--", color="0.5", zorder=0)


class Graphs:
    def lore(ax, data):
        x = data.xaxis()

        previous = 0, 0
        for i, point in enumerate(data["lore"]):
            style = "-"
            if data["easy"][i] == 1:
                style = "--"
            elif data["easy"][i] == 2:
                style = ":"

            ax.plot([previous[0], x[i]], [previous[1], point], color="C0", linestyle=style)
            previous = x[i], point

        ax.set_ylim(ymax=100)
        ax.set_ylabel("lore%")
        ax.set_title("Lore")

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

    def prototypes(ax, data):
        scatter_plot(ax, data, data["prototypes"])
        ax.set_ylabel("prototype IDs")
        ax.set_title("Prototype IDs")

    def parts(ax, data):
        scatter_plot(ax, data, data["parts"])
        ax.set_ylabel("peak state rating")
        ax.set_title("Part rating")

    def damage(ax, data):
        scatter_plot(ax, data, 100 * data["damage"] / data["turns"])
        ax.set_ylabel("damage inflicted per 100 turns")
        ax.set_title("Damage rate")

    def capacity(ax, data):
        scatter_plot(ax, data, data["capacity"])
        ax.set_ylabel("average capacity")
        ax.set_title("Inventory capacity")
        locator = matplotlib.ticker.MaxNLocator(integer=True,
                                                steps=[1, 2, 5, 10])
        ax.yaxis.set_major_locator(locator)

    def best_group(ax, data):
        scatter_plot(ax, data, data["best_group"])
        ax.set_ylabel("highest-rated group")
        ax.set_title("Ally group rating")
