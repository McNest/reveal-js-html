"""Version number for the meme bank deck (docs/memes/).

  python tools/version.py           show the next version
  python tools/version.py --write   write it into docs/memes/memes.md and
                                    docs/memes/index.html, with the version of
                                    ARJ the deck is built with
  python tools/version.py --link    link "Version 1.8.3" on the title slide to
                                    this repository on GitHub as it was at the
                                    commit that first published it

A version is year.tenth.change:
  year    1 for 2026, 2 for 2027 ...
  tenth   which tenth of the year today falls in, 0 to 9 (days 1-36 are 0,
          20 October to 25 November is 8, and so on): about every 36 days
  change  one more for every change to the slides, back to 1 when a new
          tenth starts
So 1.8.12 is the twelfth change between 20 October and 25 November 2026, and
the next tenth starts at 1.9.1. Each --write is one change: run it once for
each change, before you commit (running it twice counts two). The number is
worked out from the version already on the title slide, so it never goes
down. Commit messages start with the version ("1.8.12 Star Trek films as one
topic"), so the commits on GitHub can be matched to the versions; it prints
the number to use.

The title slide shows the month ("October 2026"); the page's metadata gets
the full date and time.

ARJ has its own version, worked out the same way by tools/version.py in the
ARJ repository (SDevTutors/apocalypse-reveal-js). --write copies it into the
page's generator line from that repository's arj/js/deck-start.js, when the
repository is cloned where ARJ_REPO says.

--link: looks for the first commit whose memes.md has this version, checks
that commit has been pushed, and only then links the version to the
repository as it was then (github.com/.../tree/SHA: browse the files at that
point, not the changes). Until then the version links to the list of
commits, so the slide never points at a commit that doesn't exist. Run it
after you push.
"""

import datetime
import os
import re
import subprocess
import sys
from urllib.parse import quote

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
MEMES = "docs/memes/memes.md"
PAGE = "docs/memes/index.html"
# The ARJ repository: C:/Users/user/GitHub/SDevTutors/apocalypse-reveal-js
ARJ_REPO = os.path.normpath(
    os.path.join(ROOT, "..", "..", "SDevTutors", "apocalypse-reveal-js")
)
GITHUB = "https://github.com/McNest/reveal-js-html/"
FIRST_YEAR = 2026

SWAPS = {
    # file to write: [(pattern, template)]
    MEMES: [
        (r'(<span class="deck-version">)[^<]*(</span>)', r"\g<1>{v}\g<2>"),
        (
            r'<time class="deck-date" datetime="[^"]*">[^<]*</time>',
            '<time class="deck-date" datetime="{stamp}">{month}</time>',
        ),
    ],
    PAGE: [
        (
            r'<meta name="version" content="[^"]*" />',
            '<meta name="version" content="{v}" />',
        ),
        # dcterms, dc-terms, DCTERMS ...: whatever prefix the page declares
        (
            r'(<meta name="[A-Za-z-]+\.modified" content=")[^"]*(" />)',
            r"\g<1>{stamp}\g<2>",
        ),
        (
            r'<meta property="article:modified_time" content="[^"]*" />',
            '<meta property="article:modified_time" content="{stamp}" />',
        ),
    ],
}


def tenth(day):
    days = 366 if datetime.date(day.year, 12, 31).timetuple().tm_yday == 366 else 365
    return (day.timetuple().tm_yday - 1) * 10 // days


def version(today, last=None):
    """The next version after last: one more change in this tenth, or the
    first change of a new one."""
    year, part = today.year - FIRST_YEAR + 1, tenth(today)
    if last and last.startswith("%d.%d." % (year, part)):
        return "%d.%d.%d" % (year, part, int(last.split(".")[2]) + 1)
    return "%d.%d.1" % (year, part)


def written():
    """The version on the title slide now."""
    text = open(os.path.join(ROOT, MEMES), encoding="utf-8").read()
    return re.search(r'<span class="deck-version">([^<]*)</span>', text).group(1)


def arj_version():
    """ARJ's version, from its repository's deck-start.js, or None."""
    path = os.path.join(ARJ_REPO, "arj", "js", "deck-start.js")
    if not os.path.exists(path):
        return None
    found = re.search(r"version: '([^']*)'", open(path, encoding="utf-8").read())
    return found and found.group(1)


def main(write):
    """Main method"""
    now = datetime.datetime.now().astimezone().replace(microsecond=0)
    today = now.date()
    v = version(today, written())
    arj = arj_version()
    print("deck %s" % v)
    print("ARJ  %s" % (arj or "not found: " + ARJ_REPO))
    if write:
        swaps = dict(SWAPS)
        if arj:
            swaps[PAGE] = swaps[PAGE] + [
                (
                    r"and (?:TAP|ARJ) [0-9.]+, (?:The Apocalypse Plugin|Apocalypse Reveal-js)",
                    "and ARJ %s, Apocalypse Reveal-js" % arj,
                )
            ]
        for target, pairs in swaps.items():
            path = os.path.join(ROOT, target)
            text = open(path, encoding="utf-8", newline="").read()
            for pattern, template in pairs:
                new = template.format(
                    v=v, stamp=now.isoformat(), month=today.strftime("%B %Y")
                )
                text, n = re.subn(pattern, new, text)
                if not n:
                    print("  not found in", target, ":", pattern)
            open(path, "w", encoding="utf-8", newline="").write(text)
    print('Commit messages start with the version: "%s <what changed>"' % v)


def link():
    """Link the title slide's version to the pushed commit that first has it."""
    path = os.path.join(ROOT, MEMES)
    text = open(path, encoding="utf-8", newline="").read()
    v = re.search(r'<span class="deck-version">([^<]*)</span>', text).group(1)
    git = lambda *args: subprocess.run(
        ["git"] + list(args), cwd=ROOT, capture_output=True, text=True
    ).stdout
    commits = git(
        "log",
        "--reverse",
        "--format=%H",
        "-S",
        '<span class="deck-version">%s</span>' % v,
        "--",
        MEMES,
        "memes.md",
    ).split()
    pushed = [c for c in commits if git("branch", "-r", "--contains", c).strip()]
    if pushed:
        url = GITHUB + "tree/" + quote(pushed[0])
    else:
        url = GITHUB + "commits/master"
        msg = "No pushed commit has version %s yet: it links to the list of commits"
        print(msg % v)

    text, n = re.subn(
        r'<a class="version-link[^"]*"[^>]*>',
        '<a class="version-link ext" href="%s">' % url,
        text,
        count=1,
    )
    open(path, "w", encoding="utf-8", newline="").write(text)
    print(
        "Version",
        v,
        "->",
        url if n else 'no <a class="version-link"> on the title slide',
    )


if __name__ == "__main__":
    if "--link" in sys.argv:
        link()
    else:
        main("--write" in sys.argv)
