import datetime

import yattag

import graphs


def timestamp():
    now = datetime.datetime.now(datetime.timezone.utc)
    return f"{now:%Y-%m-%d %H:%M %Z}"


def write_index(scores, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_dir / "style.css", "w") as style:
        style.write("""
            body {
                background: #eee;
            }

            .list {
                display: flex;
                flex-direction: column;
                align-items: center;
            }

            .list img {
                margin: 0.5em;
                max-width: 95vw;
            }""")

    doc, tag, text = yattag.Doc().tagtext()
    doc.asis("<!DOCTYPE html>")

    with tag("html"):
        with tag("head"):
            with tag("title"):
                text("Cogmind progression graphs")
            doc.stag("link", rel="stylesheet", type="text/css",
                     href="style.css")
        with tag("body"):
            with tag("h1"):
                text("Cogmind progression graphs")

            with tag("p"):
                text(f"Last updated: {timestamp()}")

            with tag("ul"):
                for player, games in sorted(scores.items(),
                                            key=lambda x: x[0].lower()):
                    with tag("li"):
                        with tag("a", href=player):
                            text(player)
                        text(f" ({len(games)} games)")

    with open(output_dir / "index.html", "w") as index:
        index.write(yattag.indent(doc.getvalue()))


def write_player_index(player, output_dir):
    doc, tag, text = yattag.Doc().tagtext()
    doc.asis("<!DOCTYPE html>")

    with tag("html"):
        with tag("head"):
            with tag("title"):
                text(f"{player}'s Cogmind progression")
            doc.stag("link", rel="stylesheet", type="text/css",
                     href="../style.css")
        with tag("body"):
            with tag("div", klass="list"):
                for graph, _ in graphs.graphs():
                    doc.stag("img", src=f"{graph}.png", alt=graph)

            with tag("p"):
                text(f"Last updated: {timestamp()}")

    with open(output_dir / "index.html", "w") as index:
        index.write(yattag.indent(doc.getvalue()))
