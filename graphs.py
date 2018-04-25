import matplotlib.ticker
import numpy as np


def line_plot(ax, data, y):
    x = data.xaxis()
    ax.plot(x, y)
    trendline(ax, x, y)


def scatter_plot(ax, data, y):
    x = data.xaxis()
    ax.scatter(x, y)
    trendline(ax, x, y)

    wins = data["win"]
    win_mask = wins >= 0
    ax.scatter(x[win_mask], y[win_mask], color="C1", label="Win")
    ax.legend(loc="upper left", prop={"size": 8})

    for i, win in enumerate(wins):
        if win > 0:
            ax.annotate(win, (x[i], y[i]), size=6, weight="bold",
                        xytext=(-2, -2.5), textcoords="offset points")


def trendline(ax, x, y):
    trend_locs = [0, ax.get_xticks()[-1]]
    trend = np.poly1d(np.polyfit(x, y, 1))
    ax.autoscale(False)
    ax.plot(trend_locs, trend(trend_locs), "--", color="0.5", zorder=0)


class Graphs:
    def lore(ax, data):
        line_plot(ax, data, data["lore"])
        ax.set_ylim(ymax=100)
        ax.set_ylabel("lore%")
        ax.set_title("Lore")

    def high_score(ax, data):
        line_plot(ax, data, data.max("score"))
        ax.set_ylabel("score")
        ax.set_title("High score")

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
