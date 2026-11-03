"""Version number for the meme bank deck (docs/memes/).

  python tools/version.py           show the version for today
  python tools/version.py --write   write it into docs/memes/memes.md and
                                    docs/memes/index.html, with the version of
                                    ARJ the deck is built with
  python tools/version.py --link    link "Version 1.8.3" on the title slide to
                                    this repository on GitHub as it was at the
                                    commit that first published it

A version is year.tenth.day, for content rather than software:
  year   1 for 2026, 2 for 2027 ...
  tenth  which tenth of the year today falls in, 0 to 9 (days 1-36 are 0,
         20 October to 25 November is 8, and so on)
  day    how many days in that tenth have had changes, counting today
So 1.8.3 is the third day of changes between 20 October and 25 November 2026.
Changes are the git commits that touch the deck's files. Run it before you
commit; running it twice on the same day gives the same number. It never
goes down: if the version already on the title slide is higher (the deck had
versions before this repository's history starts), it carries on from that.
Commit messages start with the version ("1.8.4 Star Trek films as one topic"),
so the commits on GitHub can be matched to the versions; it prints the number
to use.

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

# The deck's files, and where they were before docs/memes/, so the days with
# changes before the move still count
DECK_FILES = [
    "docs/memes",
    "memes.md",
    "memes.html",
    "src/css/memes.css",
    "src/img/topics",
]

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


def version(paths, today, last=None, last_date=None):
    """Today's version from the commits; at least one on from last (written
    on last_date), if that is in the same tenth."""
    log = subprocess.run(
        ["git", "log", "--format=%ad", "--date=short", "--"] + paths,
        cwd=ROOT,
        capture_output=True,
        text=True,
    ).stdout.split()
    days = {datetime.date.fromisoformat(d) for d in log}
    days = {
        d
        for d in days
        if d.year == today.year and tenth(d) == tenth(today) and d <= today
    }
    days.add(today)
    year, part = today.year - FIRST_YEAR + 1, tenth(today)
    day = len(days)
    if last and last.startswith("%d.%d." % (year, part)):
        day = max(day, int(last.split(".")[2]) + (last_date < today))
    return "%d.%d.%d" % (year, part, day)


def written():
    """The version on the title slide now, and the day it was written."""
    text = open(os.path.join(ROOT, MEMES), encoding="utf-8").read()
    v = re.search(r'<span class="deck-version">([^<]*)</span>', text).group(1)
    stamp = re.search(r'<time class="deck-date" datetime="([^"]*)"', text).group(1)
    return v, datetime.date.fromisoformat(stamp[:10])


def arj_version():
    """ARJ's version, from its repository's deck-start.js, or None."""
    path = os.path.join(ARJ_REPO, "arj", "js", "deck-start.js")
    if not os.path.exists(path):
        return None
    found = re.search(r"version: '([^']*)'", open(path, encoding="utf-8").read())
    return found and found.group(1)


def main(write):
    now = datetime.datetime.now().astimezone().replace(microsecond=0)
    today = now.date()
    v = version(DECK_FILES, today, *written())
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
