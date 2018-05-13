import datetime

import yattag

import graphs


def timestamp():
    now = datetime.datetime.now(datetime.timezone.utc)
    return f"{now:%Y-%m-%d %H:%M %Z}"


def build_css(rulesets):
    def build_ruleset(selector, declarations):
        ruleset = f"{selector} {{\n"

        for prop, value in declarations.items():
            ruleset += f"  {prop}: {value};\n"

        ruleset += "}\n"
        return ruleset

    return "\n".join(build_ruleset(*x) for x in rulesets.items())


def write_index(scores, output_dir, size):
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_dir / "style.css", "w") as style:
        style.write(build_css({
            "body": {
                "background": "#eee",
            },
            ".list": {
                "display": "flex",
                "flex-direction": "column",
                "align-items": "center",
            },
            ".list img": {
                "margin": "0.5em",
                "max-width": "95vw",
                "max-height": "95vh",
            },
            ".format-svg img": {
                "width": f"{size}px",
            },
        }))

    doc, tag, text = yattag.Doc().tagtext()
    doc.asis("<!DOCTYPE html>")

    with tag("html", lang="en"):
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


def write_player_index(player, output_dir, image_format):
    doc, tag, text = yattag.Doc().tagtext()
    doc.asis("<!DOCTYPE html>")

    with tag("html", lang="en"):
        with tag("head"):
            with tag("title"):
                text(f"{player}'s Cogmind progression")
            doc.stag("link", rel="stylesheet", type="text/css",
                     href="../style.css")
        with tag("body"):
            with tag("div", klass=f"list format-{image_format}"):
                for graph in graphs.graphs.keys():
                    doc.stag("img", src=f"{graph}.{image_format}", alt=graph)

            with tag("p"):
                text(f"Last updated: {timestamp()}")

    with open(output_dir / "index.html", "w") as index:
        index.write(yattag.indent(doc.getvalue()))
